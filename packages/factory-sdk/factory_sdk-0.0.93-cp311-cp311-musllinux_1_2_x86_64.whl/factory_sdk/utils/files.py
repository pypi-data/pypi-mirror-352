import os

# pasepath is user home /.factory
BASE_PATH = os.path.join(os.path.expanduser("~"), ".factory")
try:
    os.makedirs(BASE_PATH, exist_ok=True)
except Exception as e:
    raise Exception(f"Failed to create base path {BASE_PATH}. Error: {e}")


def get_local_path(resource_type, meta_id, revsion_id):
    return os.path.join(BASE_PATH, "resources", resource_type, meta_id, revsion_id)


def get_local_utility_path(utility_name, utility_type):
    return os.path.join(BASE_PATH, "utils", utility_type, utility_name)


def create_run_dir(run_id):
    run_path = os.path.join(BASE_PATH, "runs", run_id)
    os.makedirs(run_path, exist_ok=True)
    return run_path

def create_eval_dir(eval_id):
    eval_path = os.path.join(BASE_PATH, "evals", eval_id)
    os.makedirs(eval_path, exist_ok=True)
    return eval_path

def create_deployment_dir(deployment_id):
    deployment_path = os.path.join(BASE_PATH, "deployments", deployment_id)
    os.makedirs(deployment_path, exist_ok=True)
    return deployment_path