from huggingface_hub import HfApi

# from factory_sdk.logging import logger  # Removed logging as requested
from datasets import load_dataset, DatasetDict
from factory_sdk.datasets.arrow import (
    estimate_sample_size,
    save_shard,
)
import os
from factory_sdk.dto.dataset import Shard, Split
from datasets import __version__ as datasets_version
import json
from rich import print


def hf_to_factory_dataset(
    dataset_dict,
    dir,
    target_shard_size=100 * 1024 * 1024,
    max_samples_per_shard=100_000,
    num_preview_samples=10,
):
    splits = []
    for k in dataset_dict:
        os.makedirs(os.path.join(dir, k, "data"), exist_ok=True)
        estimated_bytes_per_sample = estimate_sample_size(dataset_dict[k])

        samples_per_shard = max(1, target_shard_size // estimated_bytes_per_sample)
        samples_per_shard = min(samples_per_shard, max_samples_per_shard)

        shards = []
        steps = list(range(0, len(dataset_dict[k]), samples_per_shard))

        # same preview
        save_shard(
            dataset_dict[k],
            dataset_dict[k].features,
            0,
            num_preview_samples,
            os.path.join(dir, k, "preview.parquet"),
            pbar_text=f"Saving preview for split {k}",
        )

        for ix, i in enumerate(steps):
            file = os.path.join(dir, k, "data", f"{ix}.parquet")
            current_shard_number = ix + 1
            total_shards = len(steps)
            num_samples = save_shard(
                dataset_dict[k],
                dataset_dict[k].features,
                i,
                i + samples_per_shard,
                file,
                pbar_text=f"Saving shard {current_shard_number}/{total_shards}",
            )

            shards.append(
                Shard(
                    id=f"{ix}.parquet",
                    num_samples=num_samples,
                )
            )

        split = Split(
            name=k,
            num_samples=len(dataset_dict[k]),
            features=dataset_dict[k].features.to_dict(),
            datasets_version=datasets_version,
            shards=shards,
        )

        meta_file = os.path.join(dir, k, "meta.json")
        with open(meta_file, "w") as f:
            json.dump(split.model_dump(), f, indent=2)

        splits.append(split)

    return [split.name for split in splits]


def fingerprint(name, token):
    print(
        "[bold yellow]🔍 Retrieving dataset fingerprint from HuggingFace Hub...[/bold yellow]"
    )
    api = HfApi(token=token)
    info = api.dataset_info(name)
    print(f"[bold yellow]✔ Fingerprint (SHA) retrieved: {info.sha}[/bold yellow]")
    return info.sha


def load(name, token, config, directory):
    api = HfApi(token=token)
    dataset = load_dataset(name, config, token=token)

    if not isinstance(dataset, DatasetDict):
        dataset = DatasetDict({"train": dataset})

    # save the dataset to disl
    dataset.save_to_disk(directory)

    info = api.dataset_info(name)
    return info.sha
