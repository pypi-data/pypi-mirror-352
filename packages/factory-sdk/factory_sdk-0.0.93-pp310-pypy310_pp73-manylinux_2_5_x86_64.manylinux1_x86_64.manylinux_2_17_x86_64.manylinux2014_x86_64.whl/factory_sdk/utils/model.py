from factory_sdk.dto.model import ModelInstance
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, AutoConfig, Qwen2_5_VLForConditionalGeneration
import os
from peft import get_peft_model
from accelerate import init_empty_weights
from peft import (
    PeftModelForCausalLM,
    prepare_model_for_kbit_training,
)
from rich import print
import torch

# Define model-specific attention implementation restrictions
MODEL_ATTN_RESTRICTIONS = {
    Qwen2_5_VLForConditionalGeneration: {
        "disallowed": ["flash_attention_2","sdpa"]
    }
}

def select_best_attn_impl(model:AutoModelForCausalLM):
    cuda_compute_capability = torch.cuda.get_device_capability(0)
    
    implementations={
        "flash_attention_2":(8,0),
        "sdpa":(7,5),
    }

    model_supported=[]
    #check if model cls has _supports_flash_attn_2
    if hasattr(model, "_supports_flash_attn_2") and model._supports_flash_attn_2:
        model_supported.append("flash_attention_2")
    if hasattr(model, "_supports_sdpa") and model._supports_sdpa:
        model_supported.append("sdpa")

    # Check for model-specific restrictions
    model_class = model.__class__
    if model_class in MODEL_ATTN_RESTRICTIONS:
        restrictions = MODEL_ATTN_RESTRICTIONS[model_class]
        if "disallowed" in restrictions:
            model_supported = [impl for impl in model_supported if impl not in restrictions["disallowed"]]

    supported=[]
    #check if cuda compute capability is supported
    for impl in model_supported:
        #compare tuple int, int
        if cuda_compute_capability >= implementations[impl]:
            supported.append(impl)
    supported.append("eager")

    selected_attn=supported[0]

    print(f"Selected attention implementation: {selected_attn}")

    model.config._attn_implementation=selected_attn

    return model
    

from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLConfig
AutoModelForCausalLM.register(model_class=Qwen2_5_VLForConditionalGeneration,config_class=Qwen2_5_VLConfig)

def load_empty_model(path):
    config = AutoConfig.from_pretrained(path, trust_remote_code=True)
    with init_empty_weights():
        config._attn_implementation="eager"
        return AutoModelForCausalLM.from_config(config, trust_remote_code=True)
    
    
MAX_MODEL_LENGTH = 1024*128

def _fix_tokenizer_max_length(model,tokenizer):
    #check if model conig have "max_position_embeddings", and it is set and integr
    if hasattr(model.config, "max_position_embeddings") and isinstance(model.config.max_position_embeddings, int):
        print("Set tokenizer max length to model max length")
        tokenizer.model_max_length = model.config.max_position_embeddings
    else:
        if tokenizer.model_max_length > MAX_MODEL_LENGTH:
            print(f"Set tokenizer max length to {MAX_MODEL_LENGTH}")
            tokenizer.model_max_length = MAX_MODEL_LENGTH
    return model,tokenizer

def _fix_padding_token(tokenizer):
    #check if tokenizer has padding token defined
    if tokenizer.pad_token_id is None:
        print("Set padding token to eos token")
        tokenizer.pad_token_id = tokenizer.eos_token_id

    return tokenizer




import logging
logging.getLogger("transformers_modules").setLevel(logging.ERROR)
logging.getLogger("accelerate").setLevel(logging.ERROR)


def load_model(path, peft_config, bnb_config, dtype, device="cuda"):
    # check if there is a preprocessor_config.json file
    hash_preprocessor_config = os.path.isfile(
        os.path.join(path, "preprocessor_config.json")
    )

    model = AutoModelForCausalLM.from_pretrained(
        path,
        quantization_config=bnb_config,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
        _attn_implementation="eager",
    )
    model=select_best_attn_impl(model)

    if peft_config is None:
        peft_model = model

    else:

        peft_model = get_peft_model(
            model,
            peft_config,
        )

    if hash_preprocessor_config:
        processor = AutoProcessor.from_pretrained(path, trust_remote_code=True)

        peft_model, processor.tokenizer = _fix_tokenizer_max_length(peft_model, processor.tokenizer)
        processor.tokenizer = _fix_padding_token(processor.tokenizer)


        return ModelInstance(
            model=peft_model,
            tokenizer=processor.tokenizer,
            processor=processor,
        )
    else:
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        peft_model, tokenizer = _fix_tokenizer_max_length(peft_model, tokenizer)
        tokenizer = _fix_padding_token(tokenizer)

        return ModelInstance(
            model=peft_model,
            tokenizer=tokenizer,
            processor=None,
        )


    
def load_model_for_evaluation(path, init_path, bnb_config, dtype, device="auto"):
    model = AutoModelForCausalLM.from_pretrained(
        path,
        #device_map=device, #Setting device map to auto will cause the model to fail in distributed settings (likely transformers bug!!!)
        torch_dtype=dtype,
        quantization_config=bnb_config,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        _attn_implementation="eager",
    )
    model=select_best_attn_impl(model)

    peft_model = PeftModelForCausalLM.from_pretrained(
        model, init_path, is_trainable=False, trust_remote_code=True
    )


    peft_model.eval()

    has_preprocessor_config = os.path.isfile(
        os.path.join(path, "preprocessor_config.json")
    )



    if has_preprocessor_config:
        processor = AutoProcessor.from_pretrained(path, trust_remote_code=True)

        peft_model, processor.tokenizer = _fix_tokenizer_max_length(peft_model, processor.tokenizer)
        processor.tokenizer = _fix_padding_token(processor.tokenizer)

        processor.tokenizer.padding_side = "left"
        return ModelInstance(
            model=peft_model,
            tokenizer=processor.tokenizer,
            processor=processor,
        )
    else:
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        peft_model, tokenizer = _fix_tokenizer_max_length(peft_model, tokenizer)
        tokenizer = _fix_padding_token(tokenizer)

        tokenizer.padding_side = "left"
        return ModelInstance(
            model=peft_model,
            tokenizer=tokenizer,
            processor=None,
        )


def load_model_for_training(path, init_path, bnb_config, dtype, device="cuda"):
    model = AutoModelForCausalLM.from_pretrained(
        path,
        #device_map="auto",
        torch_dtype=dtype,
        quantization_config=bnb_config,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        _attn_implementation="eager",
    )
    model=select_best_attn_impl(model)

    if bnb_config is not None:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)


    peft_model = PeftModelForCausalLM.from_pretrained(
        model, init_path, is_trainable=True, trust_remote_code=True
    )


    has_preprocessor_config = os.path.isfile(
        os.path.join(path, "preprocessor_config.json")
    )

    if has_preprocessor_config:
        processor = AutoProcessor.from_pretrained(path, trust_remote_code=True)

        peft_model, processor.tokenizer = _fix_tokenizer_max_length(peft_model, processor.tokenizer)
        processor.tokenizer = _fix_padding_token(processor.tokenizer)
        processor.tokenizer.padding_side = "right"

        return ModelInstance(
            model=peft_model,
            tokenizer=processor.tokenizer,
            processor=processor,
        )
    else:
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        peft_model, tokenizer = _fix_tokenizer_max_length(peft_model, tokenizer)
        tokenizer = _fix_padding_token(tokenizer)
        tokenizer.padding_side = "right"

        return ModelInstance(
            model=peft_model,
            tokenizer=tokenizer,
            processor=None,
        )
    

RESPONSE_TEMPLATES_CANDIDATES = [
    "<|im_start|>assistant\n",
    "<|assistant|>\n"
]


def detect_response_template(tokenizer) -> str:
    test_message = "Input Test"
    test_output = "Output Test"

    prompt1 = tokenizer.apply_chat_template(
        [
            {"role": "user", "content": test_message},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )

    for c in RESPONSE_TEMPLATES_CANDIDATES:
        if prompt1.endswith(c):
            return c

    prompt2 = tokenizer.apply_chat_template(
        [
            {"role": "user", "content": test_message},
            {"role": "assistant", "content": test_output},
        ],
        tokenize=False,
        add_generation_prompt=False,
    )

    prompt_length = len(prompt2)
    template = prompt1[prompt_length:]

    return template
