from factory_sdk.models.hf import load as load_hf, fingerprint as fingerprint_hf
from tempfile import TemporaryDirectory
from joblib import Parallel, delayed
from glob import glob
import os
from hashlib import md5
from typing import Optional, Dict
from factory_sdk.exceptions.api import NotFoundException
from factory_sdk.dto.model import ModelInitData, ModelMeta, ModelRevision, ModelObject
from factory_sdk.dto.resource import FactoryRevisionState, FactoryMetaState
from rich import print
from factory_sdk.dto.model import SUPPORTED_ARCHITECTURES
from factory_sdk.utils.files import get_local_path
from typing import Union
from urllib.parse import quote


def download_model(meta_id: str, revision_id: str, client, return_path=False):
    path = get_local_path(
        resource_type="model", meta_id=meta_id, revsion_id=revision_id
    )
    # check if finished
    finish_file = os.path.join(path, ".finished")
    if os.path.exists(finish_file):
        if return_path:
            return path
        raise NotImplementedError("return_path=False not implemented")

    # download the model
    client.download_files(
        f"models/{meta_id}/revisions/{revision_id}/files", path, scope="tenant"
    )

    # create the finish file
    with open(finish_file, "w") as f:
        f.write("ok")

    if return_path:
        return path
    raise NotImplementedError("return_path=False not implemented")


class Models:
    def __init__(self, client):
        self.client = client
        self._name=None
        self._hf_name=None
        self._hf_token=None

    def with_name(self, name: str):
        self._name = name
        return self

    def upload_model(
        self,
        factory_name: str,
        model_path: str,
        model: ModelMeta = None,
        fingerprints: Dict[str, str] = {},
    ):

        # Create a new revision
        revision: ModelRevision = self.client.post(
            f"models/{model.id}/revisions",
            {},
            response_class=ModelRevision,
            scope="tenant",
        )

        # Upload files
        files = glob(f"{model_path}/**", recursive=True)
        files = [file for file in files if os.path.isfile(file)]
        file_paths = [os.path.relpath(file, model_path) for file in files]

        print("[green]📦 Uploading files...[/green]")

        for file, file_path in zip(files, file_paths):

            self.client.upload_file(
                f"models/{model.id}/revisions/{revision.id}/files/{quote(file_path)}",
                file,
                "tenant",
            )

        # Update revision state and fingerprints
        revision.state = FactoryRevisionState.READY
        revision.fingerprints = fingerprints

        # PUT the updated revision
        revision = self.client.put(
            f"models/{model.id}/revisions/{revision.id}",
            revision,
            response_class=ModelRevision,
            scope="tenant",
        )

        # update the model
        model.last_revision = revision.id
        model.state = FactoryMetaState.READY
        model = self.client.put(
            f"models/{model.id}", model, response_class=ModelMeta, scope="tenant"
        )
        print("[bold green]🎉 Model uploaded to the Factory successfully![/bold green]")
        return model, revision

    def should_create_revision(
        self,
        hf_fingerprint: str,
        model: Optional[ModelMeta],
        revision: Optional[ModelRevision],
    ):
        if model is None:
            return True
        if revision is None:
            return True
        if revision.state == FactoryRevisionState.FAILED:
            return True
        if model.state != FactoryMetaState.READY:
            return True
        if "huggingface" not in revision.ext_fingerprints:
            return True
        if revision.ext_fingerprints["huggingface"] != hf_fingerprint:
            return True
        return False

    def from_open_weights(
        self, huggingface_name: str, huggingface_token: Optional[str] = None
    ):
        assert isinstance(huggingface_name, str), "name must be a string"
        assert isinstance(huggingface_token, str) or huggingface_token is None, "huggingface_token must be a string or None"

        from transformers import AutoConfig
        cfg:AutoConfig=AutoConfig.from_pretrained(huggingface_name,token=huggingface_token,trust_remote_code=True)
        archs=cfg.architectures
        assert len(archs)>=1, f"Model {huggingface_name} is not supported. Supported architectures are {SUPPORTED_ARCHITECTURES}"
        assert archs[0] in SUPPORTED_ARCHITECTURES, f"Model {huggingface_name} is not supported with architecture {archs[0]}. Supported architectures are {SUPPORTED_ARCHITECTURES}"
        
        self._hf_name = huggingface_name
        self._hf_token = huggingface_token
        return self
        
    def save_or_fetch(self):
        try:
            try:
                model: ModelMeta = self.client.get(
                    f"tenants/{self.client._tenant.id}/models/{self._name}",
                    response_class=ModelMeta,
                    scope="names",
                )

                if model.last_revision is not None:
                    revision: ModelRevision = self.client.get(
                        f"models/{model.id}/revisions/{model.last_revision}",
                        response_class=ModelRevision,
                        scope="tenant",
                    )
                else:
                    revision = None

            except NotFoundException:
                model: ModelMeta = self.client.post(
                    "models",
                    ModelInitData(name=self._name),
                    response_class=ModelMeta,
                    scope="tenant",
                )
                revision = None

            if revision is None:
                print("[green]🤖 Downloading model from Hugging Face...[/green]")
                with TemporaryDirectory() as tempdir:
                    new_hf_fingerprint = load_hf(self._hf_name, self._hf_token, tempdir)
                    print(f"🤖 Downloaded model {self._hf_name}")
                    model, revision = self.upload_model(
                        factory_name=self._name,
                        model_path=tempdir,
                        model=model,
                        fingerprints={"huggingface": new_hf_fingerprint},
                    )

                print(
                    f"[bold green]🎉 Model {self._name} uploaded and is READY in Factory![/bold green]"
                )

            else:
                print(
                    "[bold yellow]✅ Model already available in factory. Reuse base model.[/bold yellow]"
                )

            return ModelObject(meta=model, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to use model {self._name}[/bold red]")
            raise e

    def fetch(self, name: str, revision_id: Optional[str] = None) -> ModelObject:
        """Fetch a model by name and optional revision ID. If revision_id is not provided, the last revision will be used."""
        try:
            model: ModelMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/models/{name}",
                response_class=ModelMeta,
                scope="names",
            )

            if revision_id is None:
                if model.last_revision is None:
                    raise NotFoundException(f"No revisions found for model {name}")
                revision_id = model.last_revision

            revision: ModelRevision = self.client.get(
                f"models/{model.id}/revisions/{revision_id}",
                response_class=ModelRevision,
                scope="tenant",
            )

            return ModelObject(meta=model, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to fetch model {name}[/bold red]")
            raise e
