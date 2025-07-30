from argparse import ArgumentParser
from factory_sdk.fast.deployment.run import run
import json
from factory_sdk import FactoryClient

parser = ArgumentParser()

parser.add_argument(
    "--deployment_dir", type=str, required=True, help="Deployment directory"
)
parser.add_argument(
    "--model_path", type=str, required=True, help="Path to the model"
)
parser.add_argument(
    "--adapter_paths", type=str, required=True, help="Path to the adapter"
)
parser.add_argument(
    "--client_params", type=str, required=True, help="Client parameters"
)
parser.add_argument(
    "--deployment_name", type=str, required=True, help="Deployment name"
)


parser.add_argument(
    "--deployment_args", type=str, required=True, help="Deployment arguments"
)

parser.add_argument(
    "--recipe_paths", type=str, required=True, help="Path to the recipe"
)

parser.add_argument(
    "--deployment_structure", type=str, required=True, help="Deployment structure"
)


if __name__ == "__main__":
    args,_=parser.parse_known_args()

    from factory_sdk.dto.deployment import DeploymentArgs
    deployment_args=DeploymentArgs.model_validate(json.loads(args.deployment_args))

    from factory_sdk.fast.args import decrypt_param

    client_params=json.loads(decrypt_param(args.client_params))

    client=FactoryClient(**client_params)

    run(args,deployment_args,client)