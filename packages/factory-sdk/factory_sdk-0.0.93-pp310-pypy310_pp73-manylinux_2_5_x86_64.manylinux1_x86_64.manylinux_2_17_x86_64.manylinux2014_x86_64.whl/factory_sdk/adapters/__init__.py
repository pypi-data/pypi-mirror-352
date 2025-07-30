from factory_sdk.dto.model import ModelMeta, ModelRevision, ModelObject
from factory_sdk.dto.dataset import DatasetMeta, DatasetRevision, DatasetObject
from factory_sdk.dto.metric import MetricMeta, MetricRevision, MetricObject
from factory_sdk.dto.preprocessor import (
    PreprocessorMeta,
    PreprocessorRevision,
    PreprocessorObject,
)
from factory_sdk.dto.resource import FactoryRevisionRef
from typing import List
from factory_sdk.dto.task import TrainingTask
from factory_sdk.dto.adapter import AutoTrainingParams
from factory_sdk.fast.inspect import get_cleaned_module_source, hash_code_by_ast
from factory_sdk.exceptions.api import NotFoundException
from factory_sdk.dto.adapter import AdapterMeta, AdapterInitData, AdapterRevision, AdapterObject
from rich import print
from typing import Optional
from factory_sdk.dto.resource import FactoryMetaState, FactoryRevisionState
from hashlib import md5
from factory_sdk.dto.recipe import RecipeObject
from factory_sdk.datasets import download_dataset
from factory_sdk.dto.recipe import RecipeRevision
from factory_sdk.dto.adapter import AdapterArgs, TrainArgs, InitArgs
from factory_sdk.recipe import download_recipe
from factory_sdk.models import download_model
from factory_sdk.logging import print_exceptions
import os
from factory_sdk.utils.files import get_local_path

def download_adapter(meta_id: str, revision_id: str, client, return_path=False):
    path = get_local_path(
        resource_type="adapter", meta_id=meta_id, revsion_id=revision_id
    )

    if os.path.exists(os.path.join(path, ".finished")):
        return path

    client.download_files(f"adapters/{meta_id}/revisions/{revision_id}/files", path)

    with open(os.path.join(path, ".finished"), "w") as f:
        f.write("ok")

    return path


class Adapters:
    def __init__(self, client):
        self.client = client
        self._name = None
        self._recipe: RecipeObject = None
        self._adapter_args: AdapterArgs
        self._train_args: TrainArgs
        self._init_args: InitArgs

    def with_name(self, name: str):
        self._name = name
        return self

    def based_on_recipe(self, recipe: RecipeObject):
        self._recipe = recipe
        return self

    def using_model(self, model: ModelObject):
        self._model = model
        return self

    def with_hyperparameters(
        self,
        train_args: TrainArgs = TrainArgs(),
        adapter_args: AdapterArgs = AdapterArgs(),
        InitArgs: InitArgs = InitArgs(),
    ):
        self._adapter_args = adapter_args
        self._train_args = train_args
        self._init_args = InitArgs
        return self

    def fetch(self, name: str, revision_id: Optional[str] = None) -> AdapterObject:
        """Fetch an adapter by name and optional revision ID. If revision_id is not provided, the last revision will be used."""
        try:
            adapter: AdapterMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/adapters/{name}",
                response_class=AdapterMeta,
                scope="names",
            )

            if revision_id is None:
                if adapter.last_revision is None:
                    raise NotFoundException(f"No revisions found for adapter {name}")
                revision_id = adapter.last_revision

            revision: AdapterRevision = self.client.get(
                f"adapters/{adapter.id}/revisions/{revision_id}",
                response_class=AdapterRevision,
            )

            return AdapterObject(meta=adapter, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to fetch adapter {name}[/bold red]")
            raise e

    @print_exceptions(show_locals=False)
    def run(self):
        recipe_revision: RecipeRevision = self._recipe.get_revision()

        #check if there is already a training task
        try:
            adapter: AdapterMeta = self.client.get(
                    f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/adapters/{self._name}",
                    response_class=AdapterMeta,
                    scope="names",
                )
            

        except NotFoundException:
            print("[yellow]🤖 Adapter not found in your factory instance. Start a new training...[/yellow]")
            adapter = None

        if (
            adapter is not None
            and adapter.state == FactoryMetaState.READY
            and adapter.last_revision is not None
        ):
            revision: AdapterRevision = self.client.get(
                f"adapters/{adapter.id}/revisions/{adapter.last_revision}",
                response_class=AdapterRevision,
            )
            print(
                    "[yellow]🤖 The adapter already exists. Will you start a new training using the same name?[/yellow]"
                )
            print(
                    "[yellow]🤖 If you proceed, the existing adapter will be replaced with the results of the new training.[/yellow]"
                )
            
            print("[yellow]🤖 Do you want to proceed? (y/n)[/yellow]")
            response = input()
            if response.lower() != "y":
                print("[yellow]🤖 Proceed with the last training results.[/yellow]")
                return AdapterObject(meta=adapter, revision=revision.id)



        ##
        dataset_ref = None
        for dep in recipe_revision.dependencies:
            if dep.type == "dataset":
                dataset_ref = dep
                break
        assert dataset_ref is not None, "Dataset not found in recipe dependencies"

        #### Download the dataset ####

        model_path = download_model(
            self._model.meta.id, self._model.revision, self.client, return_path=True
        )

        dataset_path = download_dataset(
            dataset_ref.id, dataset_ref.revision, self.client, return_path=True
        )

        recipe_path = download_recipe(
            self._recipe.meta.id, recipe_revision.id, self.client, return_path=True
        )

        from factory_sdk.train.start_init import start_init
        from factory_sdk.train.start import start_training
        from uuid import uuid4
        from factory_sdk.utils.files import create_run_dir



        run_id=str(uuid4())
        run_path=create_run_dir(run_id)

        start_init(
            model_path,
            dataset_path,
            recipe_path,
            run_id,
            run_path,
            self._adapter_args,
            self._train_args,
            self._init_args,
        )

    
        client_params = self.client.get_init_params()
        return_code=start_training(
            model_path,
            self._model.meta.id,
            self._model.revision,
            dataset_path,
            recipe_path,
            self._recipe.meta.id,
            recipe_revision.id,
            run_path,
            client_params,
            self._name,
        )

        if return_code != 0:
            print("[yellow]🤖 Training failed. Please check the logs for more information.[/yellow]")
            exit(1)

        adapter: AdapterMeta = self.client.get(
            f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/adapters/{self._name}",
            response_class=AdapterMeta,
            scope="names",
        )
        return AdapterObject(meta=adapter, revision=adapter.last_revision)
