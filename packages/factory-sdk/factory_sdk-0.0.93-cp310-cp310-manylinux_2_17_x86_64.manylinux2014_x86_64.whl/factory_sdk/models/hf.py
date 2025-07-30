import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "0"

from huggingface_hub import HfApi, constants
from rich import print
from rich.progress import Progress

def fingerprint(name, token):
    print("[bold yellow]🔍 Retrieving dataset fingerprint from HuggingFace Hub...[/bold yellow]")
    api = HfApi(token=token)
    info = api.model_info(name)
    print(f"[bold yellow]✔ Fingerprint (SHA) retrieved: {info.sha}[/bold yellow]")
    return info.sha



FILE_TYPES = [
    ".py",
    ".md",
    "LICENSE",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".safetensors",
    ".model",
    ".bin",
]

SKIP_FILES = [
    ("mistralai/Mistral-7B-Instruct-v0.3","consolidated.safetensors")
]


def load(name, token, directory):
    api = HfApi(token=token)
    info = api.repo_info(name, repo_type="model")
    siblings = info.siblings

    # Filter siblings by file type
    siblings = [
        sibling
        for sibling in siblings
        if any(file_type in sibling.rfilename for file_type in FILE_TYPES)
    ]

    # filter skip files
    siblings = [
        sibling
        for sibling in siblings
        if not any(skip_file[1] in sibling.rfilename and skip_file[0] in name for skip_file in SKIP_FILES)
    ]

    # Download files sequentially with a Rich progress bar
    with Progress() as progress:
        task = progress.add_task("[green]Downloading files...", total=len(siblings))
        for sibling in siblings:
            #set the filename
            progress.update(task, description=f"[green]Downloading {sibling.rfilename}...")


            api.hf_hub_download(
                repo_id=name,
                filename=sibling.rfilename,
                repo_type="model",
                token=token,
                local_dir=directory,
                cache_dir=str(constants.HF_HUB_CACHE),
            )
            
            progress.advance(task)
    return info.sha
