from deepspeed.utils import logger
import logging

logger.setLevel(logging.ERROR)
from argparse import ArgumentParser
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments
from factory_sdk.dto.adapter import AdapterArgs, TrainArgs
import os
from transformers import BitsAndBytesConfig
from factory_sdk.utils.model import load_model_for_training
import torch
from rich import print
import json
from transformers.utils.logging import disable_progress_bar
import transformers
import warnings
from factory_sdk import FactoryClient
from factory_sdk.fast.train.dataset import load_dataset
from factory_sdk.fast.train.deepspeed import deepspeed1

warnings.filterwarnings("ignore")

transformers.logging.set_verbosity_error()
disable_progress_bar()

parser = ArgumentParser()

parser.add_argument(
    "--dataset_path", type=str, default="data", help="Directory containing the data"
)
parser.add_argument(
    "--model_path", type=str, default="model", help="Directory containing the model"
)
parser.add_argument(
    "--run_path", type=str, default="output", help="Directory for the current run"
)
parser.add_argument("--recipe_id", type=str, help="ID of the recipe")
parser.add_argument("--recipe_revision", type=str, help="Revision of the recipe")

parser.add_argument("--model_id", type=str, help="ID of the model")
parser.add_argument("--model_revision", type=str, help="Revision of the model")

parser.add_argument(
    "--recipe_path", type=str, default="recipe", help="Directory containing the recipe"
)

parser.add_argument(
    "--local_rank", type=int, default=0, help="Local rank of the process"
)
parser.add_argument("--client_params", type=str, default="{}", help="Client parameters")
parser.add_argument("--adapter_name", type=str, default="adapter", help="Adapter name")

args = parser.parse_args()


# load train and adapter args
adapter_args = AdapterArgs()

output_dir = os.path.join(args.run_path, "output")
init_path = os.path.join(args.run_path, "init")


with open(
    os.path.join(output_dir, "_factory", "config", "adapter.json"),
) as f:
    adapter_args = AdapterArgs.model_validate_json(f.read())

with open(
    os.path.join(output_dir, "_factory", "config", "train.json"),
) as f:
    train_args = TrainArgs.model_validate_json(f.read())



trainer_args = Seq2SeqTrainingArguments(
    output_dir=output_dir,
    per_device_train_batch_size=train_args.train_batch_size,
    per_device_eval_batch_size=train_args.eval_batch_size,
    gradient_accumulation_steps=train_args.gradient_accumulation_steps,
    eval_accumulation_steps=128,
    num_train_epochs=train_args.num_train_epochs,
    learning_rate=train_args.learning_rate,
    deepspeed=deepspeed1,
    report_to="none",
    logging_strategy="steps",
    logging_steps=1,
    # eval_steps=250,
    # save_steps=250,
    eval_strategy="no",
    save_strategy="no",
    predict_with_generate=False,
    disable_tqdm=True,
    warmup_ratio=train_args.warmup_ratio,
    gradient_checkpointing=train_args.gradient_checkpointing,
    #load_best_model_at_end=True,
    max_steps=train_args.max_train_steps,
    # Optimizer and learning rate related arguments
    weight_decay=train_args.weight_decay,
    adam_beta1=train_args.adam_beta1,
    adam_beta2=train_args.adam_beta2,
    adam_epsilon=train_args.adam_epsilon,
    max_grad_norm=train_args.max_grad_norm,
    lr_scheduler_type=train_args.lr_scheduler_type,
    lr_scheduler_kwargs=train_args.lr_scheduler_kwargs,
    warmup_steps=train_args.warmup_steps,
    optim=train_args.optim,
    optim_args=train_args.optim_args,
    remove_unused_columns=False,
)


# load model
with trainer_args.main_process_first():
    client = None

    if trainer_args.distributed_state.is_main_process:
        client_params = json.loads(args.client_params)
        client: FactoryClient = FactoryClient(**client_params)

        # check if the adapter exists
        from factory_sdk.dto.adapter import AdapterMeta, AdapterInitData
        from factory_sdk.exceptions.api import NotFoundException

        try:
            adapter_meta: AdapterMeta = client.get(
                f"tenants/{client._tenant.id}/projects/{client._project.id}/adapters/{args.adapter_name}",
                response_class=AdapterMeta,
                scope="names",
            )
        except NotFoundException:
            print("[yellow]🤖 Adapter not found in your factory instance...[/yellow]")
            # create a new
            adapter_meta: AdapterMeta = client.post(
                "adapters",
                AdapterInitData(name=args.adapter_name),
                response_class=AdapterMeta,
            )

    dtype = torch.float32
    if train_args.dtype == "fp16":
        dtype = torch.float16
    elif train_args.dtype == "bf16":
        dtype = torch.bfloat16

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=dtype,
        bnb_4bit_quant_storage=torch.int8,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        #llm_int8_skip_modules=adapter_args.target_modules+["lm_head"]

    )

    if train_args.quantization_bits is None:
        bnb_config = None

    model = load_model_for_training(
        args.model_path,
        init_path,
        bnb_config,
        dtype=dtype,
    )

    model.model.save_pretrained(output_dir)

    num_trainable_params = sum(
        p.numel() for p in model.model.parameters() if p.requires_grad
    )
    total_params = sum(p.numel() for p in model.model.parameters())
    trainable_percentage = (num_trainable_params / total_params) * 100

    print(f"Trainable parameters: {num_trainable_params}")
    print(f"Total parameters: {total_params}")
    print(f"Trainable percentage: {trainable_percentage:.2f}%")

    ######### load preprocessor code ########

    tokenizer = model.processor.tokenizer if model.processor else model.tokenizer
    dataset_train, dataset_test, collator = load_dataset(
        args.dataset_path, tokenizer, args.recipe_path,model.processor, train_args.max_eval_samples
    )

    num_train_samples = len(dataset_train)
    num_test_samples = len(dataset_test)

    print(f"Number of training samples: {num_train_samples}")
    print(f"Number of test samples: {num_test_samples}")

    #########################################
    tokenizer = model.processor.tokenizer if model.processor else model.tokenizer


from rich.console import Console
import torch
import logging
import json
from transformers import PrinterCallback
from factory_sdk.fast.train.callbacks.upload import CheckpointAndUploadCallback
from factory_sdk.fast.train.callbacks.statistic import StatisticsCollectionCallback


console = Console()

stats_callback = StatisticsCollectionCallback(
    model=model.model,
    track_layer_stats=False,
    log_layer_stats_every=1,
    log_gpu_every=2,
    max_train_logs=1_000,
    max_eval_logs=1_000,
    max_layer_logs=1_000,
    max_gpu_logs=1_000,
    console=console,
)

# 3. Initialize checkpoint+upload callback
upload_callback = CheckpointAndUploadCallback(
    client=client,
    adapter=adapter_meta,
    stats_callback=stats_callback,
    output_dir=output_dir,
    upload_interval_minutes=train_args.eval_every_n_minutes,
    recipe_id=args.recipe_id,
    recipe_revision=args.recipe_revision,
    model_id=args.model_id,
    model_revision=args.model_revision,
)

trainer = Seq2SeqTrainer(
    model=model.model,
    args=trainer_args,
    train_dataset=dataset_train,
    eval_dataset=dataset_test,
    data_collator=collator,
    callbacks=[stats_callback, upload_callback],
)


trainer.remove_callback(PrinterCallback)
trainer.train()

from torch import distributed as dist

if dist.is_initialized():
    dist.destroy_process_group()
