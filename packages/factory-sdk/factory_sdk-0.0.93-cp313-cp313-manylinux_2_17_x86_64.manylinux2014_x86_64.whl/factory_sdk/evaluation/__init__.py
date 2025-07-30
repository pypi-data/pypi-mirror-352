from factory_sdk.dto.adapter import AdapterObject
from factory_sdk.dto.dataset import DatasetObject
from factory_sdk.dto.recipe import RecipeObject, RecipeRevision
from factory_sdk.recipe import download_recipe
from factory_sdk.models import download_model
from factory_sdk.datasets import download_dataset
from factory_sdk.adapters import download_adapter
from factory_sdk.eval.start import start_eval
from factory_sdk.dto.evaluation import EvalArgs
from factory_sdk.utils.files import create_eval_dir
from uuid import uuid4
import os
import json
from factory_sdk.dto.evaluation import EvaluationInitData, EvaluationMeta, EvaluationRevision,EvaluationObject
from factory_sdk.exceptions.api import NotFoundException
from factory_sdk.dto.resource import FactoryMetaState, FactoryRevisionState
from glob import glob
from rich import print
from typing import Optional



class Evaluation:
    def __init__(self,client):
        self.client=client
        self._name=None
        self._adapters=[]
        self._metrics=[]
        self._recipe=None
        self._eval_args=EvalArgs()

    def with_name(self,name):
        self._name=name
        return self
    
    def for_adapter(self,adapter:AdapterObject):
        assert adapter!=None,"adapter must be provided"
        assert isinstance(adapter,AdapterObject),"adapter must be an instance of AdapterObject"
        
        self._adapters.append(adapter)
        return self

    def using_metric(self,metric,lower_is_better=False,**kwargs): # have to be a callable
        assert callable(metric),"metric must be callable"
        self._metrics.append((
            metric,
            {
                "lower_is_better":lower_is_better,
                "params":kwargs
            }
        ))

        return self

    def on_recipe(self,recipe:RecipeObject):
        assert recipe!=None,"recipe must be provided"
        assert isinstance(recipe,RecipeObject),"recipe must be an instance of RecipeObject"
        self._recipe=recipe

        return self
    
    def with_config(self,eval_args:EvalArgs):
        assert eval_args!=None,"eval_args must be provided"
        assert isinstance(eval_args,EvalArgs),"eval_args must be an instance of EvalArgs"
        self._eval_args=eval_args

        return self

    def fetch(self, name: str, revision_id: Optional[str] = None) -> EvaluationObject:
        """Fetch an evaluation by name and optional revision ID. If revision_id is not provided, the last revision will be used."""
        try:
            evaluation: EvaluationMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/evaluations/{name}",
                response_class=EvaluationMeta,
                scope="names",
            )

            if revision_id is None:
                if evaluation.last_revision is None:
                    raise NotFoundException(f"No revisions found for evaluation {name}")
                revision_id = evaluation.last_revision

            revision: EvaluationRevision = self.client.get(
                f"evaluations/{evaluation.id}/revisions/{revision_id}",
                response_class=EvaluationRevision,
            )

            return EvaluationObject(meta=evaluation, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to fetch evaluation {name}[/bold red]")
            raise e
    
    def run(self):
        #check if evaluation exists

        try:
            evaluation:EvaluationMeta=self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/evaluations/{self._name}",
                response_class=EvaluationMeta,
                scope="names"
            )
            if (
                evaluation is not None,
                evaluation.state == FactoryMetaState.READY,
                evaluation.last_revision is not None
            ):
                evaluation_revision:EvaluationRevision=self.client.get(
                    f"evaluations/{evaluation.id}/revisions/{evaluation.last_revision}",
                    response_class=EvaluationRevision
                )
                #ask for confirmation
                print(
                    "[yellow]🤖 The evaluation with already exists.  Do yo wanna rerun this evaluation?[/yellow]"
                )
                print("[yellow]🤖 Do you want to proceed? (y/n)[/yellow]")
                response=input()
                if response.lower()!="y":
                    return EvaluationObject(meta=evaluation,revision=evaluation_revision.id)
        except NotFoundException:
            evaluation=None


        recipe_revision: RecipeRevision = self._recipe.get_revision()
        
        dataset_ref = None
        for dep in recipe_revision.dependencies:
            if dep.type == "dataset":
                dataset_ref = dep
                break
        assert dataset_ref is not None, "Dataset not found in recipe dependencies"

        eval_id=str(uuid4())

        eval_dir=create_eval_dir(eval_id)

        #### loading metrics ####
        metrics_dir=os.path.join(eval_dir,"metrics")
        os.makedirs(metrics_dir,exist_ok=True)

        for metric in self._metrics:
            from factory_sdk.fast.inspect import get_cleaned_module_source
            file_path, func_name, cleaned_code=get_cleaned_module_source(metric[0])
            d=os.path.join(metrics_dir,func_name)
            os.makedirs(d,exist_ok=True)
            with open(os.path.join(d,"code.py"),"w") as f:
                f.write(cleaned_code)
            with open(os.path.join(d,"meta.json"),"w") as f:
                x={
                    "fn_name":func_name,
                    "lower_is_better":metric[1]["lower_is_better"],
                    "params":metric[1]["params"]
                }
                f.write(json.dumps(x,indent=4))



        #### Download the dataset and recipe ####

        dataset_path = download_dataset(
            dataset_ref.id, dataset_ref.revision, self.client, return_path=True
        )

        recipe_path = download_recipe(
            self._recipe.meta.id, recipe_revision.id, self.client, return_path=True
        )

        def get_model(adapter):
            model_ref = None
            adapter_ref = adapter.get_revision()
            for dep in adapter_ref.dependencies:
                if dep.type == "model":
                    model_ref = dep
                    break
            assert model_ref is not None, "Model not found in adapter dependencies"
            return model_ref

        adapter_paths=[
            {
                "path":download_adapter(
                    adapter.meta.id, adapter.revision, self.client, return_path=True
                ),
                "id":adapter.meta.id,
                "revision":adapter.revision,
                "model":{ "id":get_model(adapter).id, "revision":get_model(adapter).revision }
            }
            for adapter in self._adapters
        ]

        model_id_revisions=[]
        models=[]
        for adapter in self._adapters:
            adapter_ref = adapter.get_revision()
            model_ref = get_model(adapter)
            
            midref=model_ref.id+"#"+model_ref.revision
            if midref not in model_id_revisions:
                model_id_revisions.append(midref)
                models.append(
                    {
                        "path":download_model(
                            model_ref.id, model_ref.revision, self.client, return_path=True
                        ),
                        "id":model_ref.id,
                        "revision":model_ref.revision
                    }
                )


        
        return_code=start_eval(
            eval_dir=eval_dir,
            eval_args=self._eval_args,
            model_paths=models,
            adapter_paths=adapter_paths,
            dataset_path=dataset_path,
            recipe_path=recipe_path,
            client_params=self.client.get_init_params(),
            eval_name=self._name,
        )

        if return_code!=0:
            raise Exception("Evaluation failed")
        

        try:
            #get by name
            evaluation:EvaluationMeta=self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/evaluations/{self._name}",
                response_class=EvaluationMeta,
                scope="names"
            )
        except NotFoundException:
            #create new evaluation
            evaluation:EvaluationMeta=self.client.post(
                "evaluations",
                EvaluationInitData(
                    name=self._name
                ),
                response_class=EvaluationMeta,
            )

        #create new revision
        revision:EvaluationRevision=self.client.post(
            f"evaluations/{evaluation.id}/revisions",
            {},
            response_class=EvaluationRevision
        )

        #upload the results
        files = glob(f"{eval_dir}/**", recursive=True)
        files = [file for file in files if os.path.isfile(file)]
        file_paths = [os.path.relpath(file, eval_dir) for file in files]

        print("[green]📦 Uploading files...[/green]")
        for file, file_path in zip(files, file_paths):
            self.client.upload_file(
                f"evaluations/{evaluation.id}/revisions/{revision.id}/files/{file_path}", file
            )

        revision.state = FactoryRevisionState.READY

        # put the updated revision
        revision: EvaluationRevision = self.client.put(
            f"evaluations/{evaluation.id}/revisions/{revision.id}",
            revision,
            response_class=EvaluationRevision,
        )

        # Update the evaluation state
        evaluation.state = FactoryMetaState.READY
        evaluation.last_revision = revision.id
        evaluation: EvaluationMeta = self.client.put(
            f"evaluations/{evaluation.id}", evaluation, response_class=EvaluationMeta
        )

        return EvaluationObject(meta=evaluation,revision=revision.id)


        