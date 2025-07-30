

import os
from huggingface_hub import hf_hub_download

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def get_file(name: str):
    os.makedirs(DATA_DIR, exist_ok=True)

    file_map = {
        "sandhi_split": "sandhi_split.pth",
        "sandhi_joiner": "sandhi_joiner.pth",
        "cleaned_metres": "cleaned_metres.json",
    }

    if name not in file_map:
        raise ValueError(f"Unknown resource: {name}")

    filename = file_map[name]
    local_path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(local_path):
        print(f"🔽 Downloading {filename}...")
        hf_hub_download(
            repo_id="tanuj437/Vedika",
            filename=f"Vedika/vedika/data/{filename}",
            local_dir=DATA_DIR,
            local_dir_use_symlinks=False
        )
    return local_path
