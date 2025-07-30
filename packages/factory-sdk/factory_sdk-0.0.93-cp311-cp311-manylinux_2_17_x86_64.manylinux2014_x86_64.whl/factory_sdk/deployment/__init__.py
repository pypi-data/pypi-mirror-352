from uuid import uuid4
from factory_sdk.deployment.start import start_deployment
from factory_sdk.recipe import download_recipe
from factory_sdk.adapters import download_adapter
from factory_sdk.models import download_model
from factory_sdk.utils.files import create_deployment_dir
from factory_sdk.dto.deployment import DeploymentArgs
from factory_sdk.dto.adapter import AdapterObject
from factory_sdk.dto.model import ModelObject, ModelMeta
from threading import Thread
from transformers import AutoModelForCausalLM, AutoConfig
from peft import PeftModelForCausalLM
from accelerate import init_empty_weights
import warnings

from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLConfig
AutoModelForCausalLM.register(model_class=Qwen2_5_VLForConditionalGeneration,config_class=Qwen2_5_VLConfig)


def get_model(adapter):
            model_ref = None
            adapter_ref = adapter.get_revision()
            for dep in adapter_ref.dependencies:
                if dep.type == "model":
                    model_ref = dep
                    break
            assert model_ref is not None, "Model not found in adapter dependencies"
            return model_ref

def get_recipe(adapter):
    recipe_ref=None
    adapter_ref=adapter.get_revision()
    for dep in adapter_ref.dependencies:
        if dep.type=="recipe":
            recipe_ref=dep
            break
    assert recipe_ref is not None, "Recipe not found in adapter dependencies"
    return recipe_ref

class Deployment:
    def __init__(self, client):
        self._client=client
        self._adapters={}
        self._name=None
        self._args=DeploymentArgs()
        self.base_model_id=None

    def with_name(self, name):
        self._name=name
        return self
    
    def for_adapter(self, adapter:AdapterObject, name=None):
        assert adapter is not None, "adapter must not be None"
        assert isinstance(adapter, AdapterObject), "adapter must be an instance of AdapterObject"

        model_ref=get_model(adapter)
        base_model_id=model_ref.id+"_"+model_ref.revision

        if self.base_model_id is not None:
             assert self.base_model_id==base_model_id, "All adapters must be based on the same model"

        if name is None:
            name=adapter.meta.name
        
        i=0
        orig_name=name
        while name in self._adapters:
            i+=1
            name=f"{orig_name}_{i}"
        self._adapters[name]=adapter

        if self.base_model_id is None:
            self.base_model_id=base_model_id

        return self
    
    def with_config(self, config):
        self._args=config
        return self
    
    def run(self,daemon=True):
        adapter_paths={}
        recipe_paths={}

        adapter_infos=[]
        for key, adapter in self._adapters.items():
            adapter_paths[key]=download_adapter(
                adapter.meta.id, adapter.revision, self._client, return_path=True
            )
            adapter_infos.append({
                "name":adapter.meta.name,
                "id":adapter.meta.id,
                "revision":adapter.revision
            })
            recipe=get_recipe(adapter)

            recipe_paths[key]=download_recipe(
                recipe.id, recipe.revision, self._client, return_path=True
            )

        first_adapter=list(self._adapters.values())[0]
        model_ref=get_model(first_adapter)

        #get model meta
        model = self._client.get(
            f"models/{model_ref.id}", response_class=ModelMeta, scope="tenant"
        )
        
        # Download model once
        model_path = download_model(
            model_ref.id, model_ref.revision, self._client, return_path=True
        )
        
        # Load model config
        model_config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
        
        # Get model size information using empty weights
        with init_empty_weights():
            model_instance = AutoModelForCausalLM.from_config(model_config, trust_remote_code=True)
            base_model_info = {
                "name": model.name,
                "id": model.id,
                "revision": model_ref.revision,
                "total_params": sum(p.numel() for p in model_instance.parameters()),
                "architecture": model_config.architectures[0] if hasattr(model_config, "architectures") else None,
            }
        
        # Add adapter size information using empty weights
        adapter_infos = []
        for key, adapter in self._adapters.items():
            with init_empty_weights():
                # Suppress warnings about meta parameters during PEFT model loading
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter.*")
                    adapter_model = PeftModelForCausalLM.from_pretrained(
                        model_instance,
                        adapter_paths[key],
                        is_trainable=False,
                        trust_remote_code=True
                    )
                
                adapter_info = {
                    "name": adapter.meta.name,
                    "id": adapter.meta.id,
                    "revision": adapter.revision,
                    "total_params": sum(p.numel() for p in adapter_model.parameters()),
                }
                adapter_infos.append(adapter_info)
        
        structure = {
            "type": "model",
            "name": base_model_info["name"],
            "id": base_model_info["id"],
            "revision": base_model_info["revision"],
            "total_params": base_model_info["total_params"],
            "adapters": adapter_infos
        }

        deployment_id=str(uuid4())
        deployment_dir=create_deployment_dir(deployment_id)
        
        process=start_deployment(
            deployment_args=self._args,
            deployment_dir=deployment_dir,
            model_path=model_path,
            adapter_paths=adapter_paths,
            recipe_paths=recipe_paths,
            client_params=self._client.get_init_params(),
            deployment_name=self._name,
            deployment_structure=structure,
            daemon=daemon
        )

        return process
    
        
    
