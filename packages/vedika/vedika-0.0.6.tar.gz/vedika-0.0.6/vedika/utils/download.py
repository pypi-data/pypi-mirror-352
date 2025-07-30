from huggingface_hub import snapshot_download
import os
import shutil

# Step 1: Download snapshot with specific patterns
repo_path = snapshot_download(
    repo_id="tanuj437/Vedika",
    allow_patterns=[
        "Vedika/vedika/data/sandhi_joiner.pth",
        "Vedika/vedika/data/sandhi_split.pth",
        "Vedika/vedika/data/cleaned_metres.json",
    ]
)

# Step 2: Move downloaded files into your desired `data/` folder
target_folder = ".data"
os.makedirs(target_folder, exist_ok=True)

# Define relative paths inside repo
source_paths = [
    "Vedika/vedika/data/sandhi_joiner.pth",
    "Vedika/vedika/data/sandhi_split.pth",
    "Vedika/vedika/data/cleaned_metres.json",
]

for relative_path in source_paths:
    src = os.path.join(repo_path, relative_path)
    dst = os.path.join(target_folder, os.path.basename(relative_path))
    shutil.copy(src, dst)
    print(f"Copied {src} → {dst}")
