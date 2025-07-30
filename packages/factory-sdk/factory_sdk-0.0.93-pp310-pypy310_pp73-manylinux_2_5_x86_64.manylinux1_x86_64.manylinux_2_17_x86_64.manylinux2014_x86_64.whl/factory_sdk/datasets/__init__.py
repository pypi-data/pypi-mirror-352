from factory_sdk.datasets.hf import load as load_hf, fingerprint as fingerprint_hf
from tempfile import TemporaryDirectory
from datasets import load_from_disk, load_dataset
from joblib import Parallel, delayed
from glob import glob
import os
from hashlib import md5
from uuid import uuid4
from typing import Optional
from factory_sdk.exceptions.api import *
from factory_sdk.dto.dataset import (
    DatasetInitData,
    DatasetMeta,
    DatasetRevision,
    DatasetObject,
)
from factory_sdk.dto.resource import FactoryRevisionState, FactoryMetaState
import json
from rich import print
from PIL import Image
import base64
from io import BytesIO
from datasets import DatasetDict, Dataset
from hashlib import sha256
from factory_sdk.utils.json import CustomJSONEncoder
from factory_sdk.utils.files import get_local_path
import shutil


def download_dataset(meta_id: str, revision_id: str, client, return_path=False):
    path = get_local_path(
        resource_type="dataset", meta_id=meta_id, revsion_id=revision_id
    )
    # check if finished
    finish_file = os.path.join(path, ".finished")
    if os.path.exists(finish_file):
        if not return_path:
            return load_from_disk(path)
        return path

    # download the dataset
    client.download_files(f"datasets/{meta_id}/revisions/{revision_id}/files", path)

    # create the finish file
    with open(finish_file, "w") as f:
        f.write("ok")

    if not return_path:
        return load_from_disk(path)
    return path


def save_local(temp_path, meta_id, revision_id):
    path = get_local_path(
        resource_type="dataset", meta_id=meta_id, revsion_id=revision_id
    )
    os.makedirs(path, exist_ok=True)
    # move the file from temp to path, dont copy the source folder
    # Move all contents from A to B
    for item in os.listdir(temp_path):
        source = os.path.join(temp_path, item)
        destination = os.path.join(path, item)
        shutil.move(source, destination)

    with open(os.path.join(path, ".finished"), "w") as f:
        f.write("ok")


class NamedDatasetConnector:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.dataset = None

    def upload_dataset(
        self,
        factory_name,
        dataset_path,
        dataset: Optional[DatasetMeta],
        fingerprints={},
    ):
        if dataset is None:
            print(
                "[green]🤖 Creating a new dataset in your factory instance...[/green]"
            )
            dataset: DatasetMeta = self.client.post(
                "datasets",
                DatasetInitData(name=factory_name),
                response_class=DatasetMeta,
            )

        revision: DatasetRevision = self.client.post(
            f"datasets/{dataset.id}/revisions", {}, response_class=DatasetRevision
        )

        files = glob(f"{dataset_path}/**", recursive=True)
        files = [file for file in files if os.path.isfile(file)]
        file_paths = [os.path.relpath(file, dataset_path) for file in files]

        print("[green]📦 Uploading files...[/green]")
        for file, file_path in zip(files, file_paths):
            self.client.upload_file(
                f"datasets/{dataset.id}/revisions/{revision.id}/files/{file_path}", file
            )

        revision.state = FactoryRevisionState.READY

        revision.fingerprints = fingerprints

        # put the updated revision
        revision: DatasetRevision = self.client.put(
            f"datasets/{dataset.id}/revisions/{revision.id}",
            revision,
            response_class=DatasetRevision,
        )

        # Update the dataset state
        dataset.state = FactoryMetaState.READY
        dataset.last_revision = revision.id
        dataset: DatasetMeta = self.client.put(
            f"datasets/{dataset.id}", dataset, response_class=DatasetMeta
        )

        save_local(dataset_path, dataset.id, revision.id)

        print(
            "[bold green]🎉 Dataset uploaded to the Factory successfully![/bold green]"
        )
        return dataset, revision

    def create_test_samples(self, dataset_path, max_samples=100):
        dataset = load_from_disk(dataset_path)
        splits = [k for k in dataset]
        test_dict = {}
        for k in splits:
            if len(dataset[k]) > max_samples:
                test_data = dataset[k].train_test_split(test_size=max_samples, seed=42)[
                    "test"
                ]
            else:
                test_data = dataset[k]
            test_dict[k] = test_data

        test_dataset = DatasetDict(test_dict)

        test_sample_path = f"{dataset_path}/_factory/test_samples"
        test_dataset.save_to_disk(test_sample_path)

    def create_preview(self, dataset_path, max_samples=20):
        dataset = load_from_disk(dataset_path)

        splits = [k for k in dataset]
        for k in splits:
            split = dataset[k]
            if len(split) > max_samples:
                dataset[k] = split.select(list(range(max_samples)))

            rows = [x for x in dataset[k]]

            preview_path = f"{dataset_path}/_factory/preview/{k}/data.json"
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            with open(preview_path, "w") as f:
                json.dump(rows, f, cls=CustomJSONEncoder, indent=2)

    def from_local(self, local_dataset):
        self.local_dataset = local_dataset
        return self

    def save_or_fetch(self):

        local_dataset = self.local_dataset
        # assert that the dataset is a dataset or dataset dict
        assert isinstance(
            local_dataset, DatasetDict
        ), "The dataset must be a dataset dict"
        # assert that train and test splits are present
        assert (
            "train" in local_dataset and "test" in local_dataset
        ), "The dataset must have train and test splits"

        fingerprints = []
        for k in local_dataset:
            fp = local_dataset[k]._fingerprint
            fp_bytes = bytes.fromhex(fp)
            fingerprints.append(fp_bytes)
        fingerprints = sorted(fingerprints)

        digest = sha256()
        for fp in fingerprints:
            digest.update(fp)

        fingerprint = digest.hexdigest()

        try:
            dataset: DatasetMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/datasets/{self.name}",
                response_class=DatasetMeta,
                scope="names",
            )
        except NotFoundException:
            print("[yellow]🤖 Dataset not found in your factory instance...[/yellow]")
            dataset = None

        if (
            dataset is not None
            and dataset.state == FactoryMetaState.READY
            and dataset.last_revision is not None
        ):
            revision: DatasetRevision = self.client.get(
                f"datasets/{dataset.id}/revisions/{dataset.last_revision}",
                response_class=DatasetRevision,
            )

            if revision.fingerprints.get("dataset") == fingerprint:
                return DatasetObject(meta=dataset, revision=revision.id)
            else:
                # ask for confirmation
                print(
                    "[yellow]🤖 The dataset has been updated since the last upload. Do you want to upload the updated dataset?[/yellow]"
                )
                print(
                    "[yellow]🤖 If you proceed, the existing dataset will be replaced with the updated dataset.[/yellow]"
                )
                print("[yellow]🤖 Do you want to proceed? (y/n)[/yellow]")
                response = input()
                if response.lower() != "y":
                    print("[yellow]🤖 Dataset upload cancelled.[/yellow]")
                    exit()

        ### Load the dataset from HuggingFace and upload it to the Factory ###
        with TemporaryDirectory() as tempdir:

            if isinstance(local_dataset, Dataset):
                # if dataset is only dataset object -> convert to dataset dict
                local_dataset = DatasetDict({"train:": local_dataset})

            local_dataset.save_to_disk(tempdir)

            self.create_test_samples(tempdir)

            self.create_preview(tempdir)

            dataset, revision = self.upload_dataset(
                self.name,
                tempdir,
                dataset,
                fingerprints={"dataset": fingerprint},
            )

        # fetch the dataset
        dataset: DatasetMeta = self.client.get(
            f"datasets/{dataset.id}",
            response_class=DatasetMeta,
        )

        # assert that revision is inside the dataset.revisions
        assert (
            len([r for r in dataset.revisions if r.id == revision.id]) > 0
        ), "The revision is not inside the dataset revisions"

        return DatasetObject(meta=dataset, revision=revision.id)


class Dataset:
    def __init__(self, client):
        self.client = client

    def with_name(self, name) -> NamedDatasetConnector:
        return NamedDatasetConnector(self.client, name=name)

    def fetch(self, name: str, revision_id: Optional[str] = None) -> DatasetObject:
        """Fetch a dataset by name and optional revision ID. If revision_id is not provided, the last revision will be used."""
        try:
            dataset: DatasetMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/datasets/{name}",
                response_class=DatasetMeta,
                scope="names",
            )

            if revision_id is None:
                if dataset.last_revision is None:
                    raise NotFoundException(f"No revisions found for dataset {name}")
                revision_id = dataset.last_revision

            revision: DatasetRevision = self.client.get(
                f"datasets/{dataset.id}/revisions/{revision_id}",
                response_class=DatasetRevision,
            )

            return DatasetObject(meta=dataset, revision=revision.id)
        except Exception as e:
            print(f"[bold red]❌ Failed to fetch dataset {name}[/bold red]")
            raise e
