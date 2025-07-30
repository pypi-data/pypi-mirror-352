from factory_sdk.fast.train.initialize import initialize_adapter
from argparse import ArgumentParser
from factory_sdk.dto.adapter import TrainArgs, AdapterArgs, InitArgs


parser=ArgumentParser()

parser.add_argument("--adapter-args", type=str, required=True)
parser.add_argument("--train-args", type=str, required=True)
parser.add_argument("--init-args", type=str, required=True)
parser.add_argument("--model-path", type=str, required=True)
parser.add_argument("--dataset-path", type=str, required=True)
parser.add_argument("--recipe-path", type=str, required=True)
parser.add_argument("--run-id", type=str, required=True)
parser.add_argument("--run-dir", type=str, required=True)

args=parser.parse_args()

adapter_args = AdapterArgs.model_validate_json(args.adapter_args)
train_args = TrainArgs.model_validate_json(args.train_args)
init_args = InitArgs.model_validate_json(args.init_args)

initialize_adapter(
    args=adapter_args,
    train_args=train_args,
    init_args=init_args,
    model_path=args.model_path,
    dataset_path=args.dataset_path,
    recipe_path=args.recipe_path,
    run_id=args.run_id,
    run_dir=args.run_dir,
)


