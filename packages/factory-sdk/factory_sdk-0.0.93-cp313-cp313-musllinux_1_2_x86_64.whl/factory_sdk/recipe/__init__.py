from typing import Any, Callable, Dict, Optional
import os
import json
import numpy as np
from rich import print
from tqdm.auto import tqdm
from datasets import load_from_disk
from glob import glob
from tempfile import TemporaryDirectory
from hashlib import sha256

from factory_sdk.dto.dataset import DatasetObject
from factory_sdk.dto.model import ModelChatInput
from factory_sdk.dto.recipe import (
    RecipeMeta,
    RecipeRevision,
    RecipeObject,
    RecipeInitData,
    DatasetRef,
)
from factory_sdk.dto.preprocessor import PreprocessorCode
from factory_sdk.fast.ood import OODPipeline
from factory_sdk.fast.inspect import (
    get_cleaned_module_source,
    hash_code_by_ast,
    load_code_from_string,
)
from factory_sdk.utils.files import get_local_path
from factory_sdk.utils.json import CustomJSONEncoder
from factory_sdk.exceptions.api import NotFoundException
from factory_sdk.dto.resource import (
    FactoryMetaState,
    FactoryRevisionState,
    FactoryResourceRef,
)
from factory_sdk.datasets import download_dataset
from factory_sdk.utils.dict import clean_dict
from factory_sdk.fast.ood.embeddings import compute_embeddings
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


def download_recipe(meta_id: str, revision_id: str, client, return_path=False):
    path = get_local_path(
        resource_type="recipe", meta_id=meta_id, revsion_id=revision_id
    )

    if os.path.exists(os.path.join(path, ".finished")):
        return path if return_path else load_from_disk(path)

    client.download_files(f"recipes/{meta_id}/revisions/{revision_id}/files", path)

    with open(os.path.join(path, ".finished"), "w") as f:
        f.write("ok")

    return path if return_path else load_from_disk(path)


class RecipeBuilder:
    def __init__(self, client):
        self.client = client
        self._name = None
        self._dataset = None
        self._preprocessor = None
        self._preprocessor_samples = None
        self.ood_embeddings = None

    def with_name(self, name: str) -> "RecipeBuilder":
        self._name = name
        return self

    def using_dataset(self, dataset: DatasetObject) -> "RecipeBuilder":
        self._dataset = dataset
        return self

    def with_preprocessor(self, preprocessor: Callable) -> "RecipeBuilder":
        path, fn_name, source_code = get_cleaned_module_source(preprocessor)
        self._preprocessor = PreprocessorCode(code=source_code, fn_name=fn_name)
        return self

    def fetch(self, name: str, revision_id: Optional[str] = None) -> RecipeObject:
        """Fetch a recipe by name and optional revision ID. If revision_id is not provided, the last revision will be used."""
        try:
            recipe: RecipeMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/recipes/{name}",
                response_class=RecipeMeta,
                scope="names",
            )

            if revision_id is None:
                if recipe.last_revision is None:
                    raise NotFoundException(f"No revisions found for recipe {name}")
                revision_id = recipe.last_revision

            revision: RecipeRevision = self.client.get(
                f"recipes/{recipe.id}/revisions/{revision_id}",
                response_class=RecipeRevision,
            )

            return RecipeObject(meta=recipe, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to fetch recipe {name}[/bold red]")
            raise e

    def _validate_preprocessor(self, directory: str):
        reloaded_fn = load_code_from_string(
            self._preprocessor.code, self._preprocessor.fn_name
        )
        dataset = download_dataset(
            self._dataset.meta.id, self._dataset.revision, self.client
        )
        self._preprocessor_samples = self._gen_preprocessed_samples(
            dataset, reloaded_fn
        )

        # Save preview samples
        preview_dir = os.path.join(directory, "_factory", "preview")
        os.makedirs(preview_dir, exist_ok=True)
        for k in self._preprocessor_samples:
            data_file = os.path.join(preview_dir, f"{k}/data.json")
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, "w") as f:
                json.dump(
                    self._preprocessor_samples[k], f, cls=CustomJSONEncoder, indent=4
                )

        embed_config = {
            "text_model_name": "intfloat/multilingual-e5-small",
            "image_model_name": "sentence-transformers/clip-ViT-B-32",
            "text_prefix": "query: ",
            "max_samples": 5_000,
        }

        # Updated to unpack all four return values from compute_embeddings
        text_train_embeddings, image_train_embeddings, text_train_roles, image_train_roles = compute_embeddings(
            dataset["train"], reloaded_fn, **embed_config
        )

        text_test_embeddings, image_test_embeddings, text_test_roles, image_test_roles = compute_embeddings(
            dataset["test"], reloaded_fn, **embed_config
        )

        print("Compare Distributions of Train and Test Data...")
        text_ood = OODPipeline(
            text_train_embeddings,
        )
        image_ood = None
        if image_train_embeddings is not None:
            image_ood = OODPipeline(
                image_train_embeddings,
            )

        text_result = text_ood.detect_shift(text_test_embeddings)
        image_result = None
        if image_test_embeddings is not None:
            image_result = image_ood.detect_shift(image_test_embeddings)

        ood_dir = os.path.join(directory, "data", "distribution")
        os.makedirs(ood_dir, exist_ok=True)

        # Save config
        config_path = os.path.join(ood_dir, "test_config.json")
        with open(config_path, "w") as f:
            json.dump({"embeddings": embed_config}, f, indent=4)

        with open(os.path.join(ood_dir, "test_result.json"), "w") as f:
            json.dump(
                {
                    "text": text_result.model_dump(),
                    "image": (
                        image_result.model_dump() if image_result is not None else None
                    ),
                },
                f,
                indent=4,
            )

        # compute 2d points
        p2d = OODPipeline.compute_2d(
            {"text": text_train_embeddings, "image": image_train_embeddings},
            {"text": text_test_embeddings, "image": image_test_embeddings},
        )

        # Save split data
        for split, split_embeddings, split_roles in [
            ("train", 
             {"text": text_train_embeddings, "image": image_train_embeddings},
             {"text": text_train_roles, "image": image_train_roles}),
            ("test", 
             {"text": text_test_embeddings, "image": image_test_embeddings},
             {"text": text_test_roles, "image": image_test_roles})
        ]:
            split_dir = os.path.join(ood_dir, split)
            os.makedirs(split_dir, exist_ok=True)

            # Save 2D points
            points = p2d[split]
            points_path = os.path.join(split_dir, "points.npz")
            points = clean_dict(points)
            np.savez_compressed(points_path, **points, allow_pickle=False)

            # save embeddings and roles together in the same npz file
            embeddings_path = os.path.join(split_dir, "embeddings.npz")
            
            # Prepare data dictionary with both embeddings and roles
            data_dict = {}
            
            # Add embeddings
            embeddings = clean_dict(split_embeddings)
            for key, value in embeddings.items():
                if value is not None:
                    data_dict[f"{key}_embeddings"] = value
                
            # Add roles - now they're already integers so we can store them directly
            roles = clean_dict(split_roles)
            for key, value in roles.items():
                if value is not None:
                    # Convert role lists to numpy arrays for storage
                    data_dict[f"{key}_roles"] = np.array(value, dtype=np.int32)
            
            # Save combined data - no need for allow_pickle now
            np.savez_compressed(embeddings_path, **data_dict)

    def _gen_preprocessed_samples(
        self, dataset: Any, fn: Callable, max_samples: int = 20
    ) -> Dict:
        results = {}
        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            for split in dataset:
                task=progress.add_task(f"Processing split {split}", total=len(dataset[split]))
                results[split] = []
                for i in range(len(dataset[split])):
                    try:
                        result = fn(dataset[split][i])
                        if not isinstance(result, ModelChatInput):
                            raise TypeError(
                                f"Expected ModelChatInput but got {type(result)}"
                            )
                        if len(results[split]) < max_samples:
                            results[split].append(
                                {"input": dataset[split][i], "output": result.model_dump()}
                            )
                        progress.update(task, advance=1)
                    except Exception as e:
                        print(f"Preprocessor failed for {split} split at index {i}")
                        raise e
            
        return results

    def _validate_all(self, directory: str):
        if not self._name or not isinstance(self._name, str) or len(self._name) < 1:
            raise ValueError("Name must be a non-empty string")
        if not self._dataset or not isinstance(self._dataset, DatasetObject):
            raise ValueError("Dataset must be a valid DatasetObject")
        if not self._preprocessor:
            raise ValueError("Preprocessor must be set")
        self._validate_preprocessor(directory)

    # Rest of the RecipeBuilder class remains the same
    def save_or_fetch(self) -> RecipeObject:
        # Handle recipe upload
        preprocessor_fp = hash_code_by_ast(self._preprocessor.code)
        dataset_fp = self._dataset_fp()
        fp_bytes = sorted([bytes.fromhex(preprocessor_fp), bytes.fromhex(dataset_fp)])

        fingerprint = sha256()
        for fp in fp_bytes:
            fingerprint.update(fp)
        fingerprint = fingerprint.hexdigest()

        # Check existing recipe
        try:
            recipe = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/recipes/{self._name}",
                response_class=RecipeMeta,
                scope="names",
            )
            if recipe.last_revision is not None:
                revision: RecipeRevision = self.client.get(
                    f"recipes/{recipe.id}/revisions/{recipe.last_revision}",
                    response_class=RecipeRevision,
                )
                if (
                    "resources" in revision.fingerprints
                    and revision.fingerprints["resources"] == fingerprint
                ):
                    return RecipeObject(meta=recipe, revision=revision.id)
                else:
                    print(
                        "[yellow]🤖 The recipe has been updated since the last upload. Do you want to upload the updated recipe?[/yellow]"
                    )
                    print(
                        "[yellow]🤖 If you proceed, a new revision will be created.[/yellow]"
                    )
                    print("[yellow]🤖 Do you want to proceed? (y/n)[/yellow]")
                    response = input()
                    if response.lower() != "y":
                        print("[yellow]Use old recipe[/yellow]")
                        return RecipeObject(meta=recipe, revision=revision.id)
        except NotFoundException:
            recipe = None

        with TemporaryDirectory() as temp_dir:
            # Validate and generate data
            if not self._name or not isinstance(self._name, str) or len(self._name) < 1:
                raise ValueError("Name must be a non-empty string")
            if not self._dataset or not isinstance(self._dataset, DatasetObject):
                raise ValueError("Dataset must be a valid DatasetObject")
            if not self._preprocessor:
                raise ValueError("Preprocessor must be set")

            # Run validation and generate data
            self._validate_preprocessor(temp_dir)

            # Save preprocessor code
            preprocessor_dir = os.path.join(temp_dir, "preprocessor")
            os.makedirs(preprocessor_dir, exist_ok=True)
            with open(os.path.join(preprocessor_dir, "code.py"), "w") as f:
                f.write(self._preprocessor.code)
            with open(os.path.join(preprocessor_dir, "meta.json"), "w") as f:
                json.dump({"fn_name": self._preprocessor.fn_name}, f)

            # Save meta
            meta = {
                "dataset": {
                    "meta": self._dataset.meta.id,
                    "revision": self._dataset.revision,
                }
            }
            with open(os.path.join(temp_dir, "meta.json"), "w") as f:
                json.dump(meta, f, indent=4)

            # Upload new recipe/revision
            fingerprints = {
                "resources": fingerprint,
                "dataset": dataset_fp,
                "preprocessor": preprocessor_fp,
            }
            dataset_ref = DatasetRef(
                meta=self._dataset.meta.id, revision=self._dataset.revision
            )
            preprocessor, revision = self._upload(
                self._name, temp_dir, recipe, fingerprints, dataset_ref
            )
            return RecipeObject(meta=preprocessor, revision=revision.id)

    def _dataset_fp(self) -> str:
        dataset = self._dataset
        revisions = dataset.meta.revisions
        revision_id = dataset.revision

        revision = None
        for rev in revisions:
            if rev.id == revision_id:
                revision = rev
                break

        if revision is None:
            raise ValueError(
                f"Revision {revision_id} not found in dataset {dataset.meta.id}"
            )

        fingerprints = revision.fingerprints
        if "dataset" not in fingerprints:
            raise ValueError(
                "Dataset fingerprint not found in revision {revision_id}. Please re-upload the dataset this is needed to compute the recipe fingerprint"
            )

        return fingerprints["dataset"]

    def _save_preprocessor(self, dir: str):
        preprocessor_dir = os.path.join(dir, "preprocessor")
        os.makedirs(preprocessor_dir, exist_ok=True)

        with open(os.path.join(preprocessor_dir, "code.py"), "w") as f:
            f.write(self._preprocessor.code)
        with open(os.path.join(preprocessor_dir, "meta.json"), "w") as f:
            json.dump({"fn_name": self._preprocessor.fn_name}, f)

        preview_dir = os.path.join(dir, "_factory", "preview")
        os.makedirs(preview_dir, exist_ok=True)
        for k in self._preprocessor_samples:
            data_file = os.path.join(preview_dir, f"{k}/data.json")
            os.makedirs(os.path.dirname(data_file), exist_ok=True)
            with open(data_file, "w") as f:
                json.dump(
                    self._preprocessor_samples[k], f, cls=CustomJSONEncoder, indent=4
                )

    def _save_meta(self, dir: str):
        meta = {
            "dataset": {
                "meta": self._dataset.meta.id,
                "revision": self._dataset.revision,
            },
            "checks": ["ood"],
            "preprocessor": {
                "fingerprint": {"value": hash_code_by_ast(self._preprocessor.code)}
            },
        }
        with open(os.path.join(dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=4)

    def _upload(
        self,
        factory_name: str,
        path: str,
        recipe: RecipeMeta = None,
        fingerprints={},
        dataset_ref=None,
    ):
        if recipe is None:
            print("[green]🤖 Creating a new recipe in your factory instance...[/green]")
            recipe = self.client.post(
                "recipes", RecipeInitData(name=factory_name), response_class=RecipeMeta
            )

        revision = self.client.post(
            f"recipes/{recipe.id}/revisions", {}, response_class=RecipeRevision
        )

        files = [f for f in glob(f"{path}/**", recursive=True) if os.path.isfile(f)]
        file_paths = [os.path.relpath(f, path) for f in files]

        print("[green]📦 Uploading files...[/green]")
        for file, file_path in zip(files, file_paths):
            self.client.upload_file(
                f"recipes/{recipe.id}/revisions/{revision.id}/files/{file_path}", file
            )

        revision.state = FactoryRevisionState.READY
        revision.fingerprints = fingerprints

        revision.dependencies = [
            FactoryResourceRef(
                id=dataset_ref.meta, revision=dataset_ref.revision, type="dataset"
            )
        ]

        revision = self.client.put(
            f"recipes/{recipe.id}/revisions/{revision.id}",
            revision,
            response_class=RecipeRevision,
        )

        recipe.state = FactoryMetaState.READY
        recipe.last_revision = revision.id
        recipe = self.client.put(
            f"recipes/{recipe.id}", recipe, response_class=RecipeMeta
        )

        # fetch the recipe (bugfix should be return by put call correctly)
        recipe = self.client.get(f"recipes/{recipe.id}", response_class=RecipeMeta)

        print(
            "[bold green]🎉 Recipe published to the Factory successfully![/bold green]"
        )
        return recipe, revision
