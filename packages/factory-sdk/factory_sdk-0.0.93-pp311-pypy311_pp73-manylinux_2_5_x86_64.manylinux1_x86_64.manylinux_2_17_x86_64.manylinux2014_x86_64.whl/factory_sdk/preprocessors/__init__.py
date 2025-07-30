from factory_sdk.fast.inspect import (
    get_cleaned_module_source,
    hash_code_by_ast,
    load_code_from_string,
    find_dependencies,
)
import json
from hashlib import md5
from factory_sdk.dto.preprocessor import (
    PreprocessorMeta,
    PreprocessorRevision,
    PreprocessorInitData,
    PreprocessorCallObject,
    PreprocessorObject,
)
from factory_sdk.exceptions.api import NotFoundException
from typing import Optional
from factory_sdk.dto.resource import FactoryMetaState, FactoryRevisionState
from factory_sdk.logging import print
from tempfile import TemporaryDirectory
from glob import glob
from joblib import Parallel, delayed
import os
from factory_sdk.dto.dataset import DatasetObject
import tempfile
from datasets import load_from_disk
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from factory_sdk.dto.model import ModelChatInput
from factory_sdk.logging import print_exceptions
from factory_sdk.utils.json import CustomJSONEncoder


class PreprocessorWithName:
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def for_dataset(self, dataset: DatasetObject):
        assert isinstance(
            dataset, DatasetObject
        ), f"Expected DatasetObject but got {type(dataset)}"
        return PreprocessorForDatasetWithName(self.client, self.name, dataset)


class Preprocessors:
    def __init__(self, client):
        self.client = client

    def with_name(self, name):
        return PreprocessorWithName(self.client, name)


class PreprocessorForDatasetWithName:
    def __init__(self, client, name, dataset):
        self.client = client
        self.name: str = name
        self.dataset = dataset

    def load_sample_data(self, target_path):
        self.client.download_file_or_directory(
            f"datasets/{self.dataset.meta.id}/revisions/{self.dataset.revision.id}/files/_factory/test_samples",
            target_path,
        )

    def test_implementation(
        self, fn, dir_dataset, dir_output, code, fn_name, max_samples=20
    ):
        dataset = load_from_disk(dir_dataset)
        results = {}

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            for split in dataset:
                results[split] = []
                total_items = len(dataset[split])
                task = progress.add_task(
                    f"Processing split [{split}]", 
                    total=total_items
                )
                
                for i in range(total_items):
                    try:
                        result_train = fn(dataset[split][i])
                        assert isinstance(
                            result_train, ModelChatInput
                        ), f"Expected TrainModelInstructInput but got {type(result_train)}"
                        results[split].append(result_train.model_dump())
                    except Exception as e:
                        print(
                            f"Testing preprocessor failed in training mode for split {split} and index {i}"
                        )
                        print(f"Code: {code}")
                        raise e
                    progress.update(task, advance=1)

        # remove image from dict if there is no image in the whole dataset
        for k in results:
            file = f"{dir_output}/_factory/preview/{k}/data.json"
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "w") as f:
                json.dump(results[k], f, cls=CustomJSONEncoder, indent=4)

    def upload_preprocessor(
        self,
        factory_name,
        preprocessor_path,
        preprocessor: Optional[PreprocessorObject],
        fingerprints={},
    ):
        if preprocessor is None:
            print(
                "[green]🤖 Creating a new preprocessor in your factory instance...[/green]"
            )
            preprocessor: PreprocessorMeta = self.client.post(
                "preprocessors",
                PreprocessorInitData(name=factory_name),
                response_class=PreprocessorMeta,
            )

        revision: PreprocessorRevision = self.client.post(
            f"preprocessors/{preprocessor.id}/revisions",
            {},
            response_class=PreprocessorRevision,
        )

        files = glob(f"{preprocessor_path}/**", recursive=True)
        files = [file for file in files if os.path.isfile(file)]
        file_paths = [os.path.relpath(file, preprocessor_path) for file in files]

        with Progress(
            SpinnerColumn(),
            *Progress.get_default_columns(),
            TimeElapsedColumn(),
        ) as progress:
            upload_task = progress.add_task(
                "[green]📦 Uploading files...", 
                total=len(files)
            )
            
            for file, file_path in zip(files, file_paths):
                self.client.upload_file(
                    f"preprocessors/{preprocessor.id}/revisions/{revision.id}/files/{file_path}",
                    file,
                )
                progress.update(upload_task, advance=1)

        revision.state = FactoryRevisionState.READY
        revision.fingerprints = fingerprints

        # put the updated revision
        revision: PreprocessorRevision = self.client.put(
            f"preprocessors/{preprocessor.id}/revisions/{revision.id}",
            revision,
            response_class=PreprocessorRevision,
        )

        # Update the meta state
        preprocessor.state = FactoryMetaState.READY
        preprocessor.last_revision = revision.id
        preprocessor: PreprocessorMeta = self.client.put(
            f"preprocessors/{preprocessor.id}",
            preprocessor,
            response_class=PreprocessorMeta,
        )

        print(
            "[bold green]🎉 Preprocessor uploaded to the Factory successfully![/bold green]"
        )
        return preprocessor, revision

    @print_exceptions(show_locals=False)
    def from_code(self, ref):
        # Extract code and compute fingerprint
        path, fn_name, code__src = get_cleaned_module_source(ref)
        fingerprint = hash_code_by_ast(code__src)

        # Try to fetch the preprocessor
        try:
            preprocessor: PreprocessorMeta = self.client.get(
                f"tenants/{self.client._tenant.id}/projects/{self.client._project.id}/preprocessors/{self.name}",
                response_class=PreprocessorMeta,
                scope="names",
            )
            if preprocessor.last_revision is not None:
                revision: PreprocessorRevision = self.client.get(
                    f"preprocessors/{preprocessor.id}/revisions/{preprocessor.last_revision}",
                    response_class=PreprocessorRevision,
                )

                if revision.fingerprints.get("code") == fingerprint:
                    return PreprocessorObject(meta=preprocessor, revision=revision)
        except NotFoundException:
            preprocessor = None

        # load the code from code_src (string)
        reloaded_fn = load_code_from_string(code__src, fn_name)

        # Create a temporary directory to store code and params
        with TemporaryDirectory() as dir:
            # test the implementation
            print("[green]🧪 Testing the preprocessor implementation...[/green]")
            with TemporaryDirectory() as dir2:
                self.load_sample_data(dir2)
                self.test_implementation(reloaded_fn, dir2, dir, reloaded_fn, fn_name)
                print(
                    "[bold green]🎉 Preprocessor implementation passed all tests![/bold green]"
                )

            # Write the source code
            code_file = f"{dir}/code.py"
            with open(code_file, "w") as f:
                f.write(code__src)

            packages = find_dependencies(code_file)
            # Write the call parameters
            with open(f"{dir}/meta.json", "w") as f:
                f.write(
                    PreprocessorCallObject(
                        fn_name=fn_name, packages=packages
                    ).model_dump_json(indent=4)
                )

            self.upload_preprocessor(
                self.name, dir, preprocessor, fingerprints={"code": fingerprint}
            )