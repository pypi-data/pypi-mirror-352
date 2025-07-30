from huggingface_hub import snapshot_download
import os
import shutil
import vedika  # Ensure the package is installed and importable

# Step 1: Locate Vedika's install directory
vedika_root = os.path.dirname(vedika.__file__)  # e.g., .../site-packages/vedika
data_dir = os.path.join(vedika_root, "data")
os.makedirs(data_dir, exist_ok=True)

# Step 2: Download selected files from Hugging Face
repo_path = snapshot_download(
    repo_id="tanuj437/Vedika",
    allow_patterns=[
        "Vedika/vedika/data/sandhi_joiner.pth",
        "Vedika/vedika/data/sandhi_split.pth",
        "Vedika/vedika/data/cleaned_metres.json",
    ]
)

# Step 3: Copy files into the vedika installed `data` directory
source_paths = [
    "Vedika/vedika/data/sandhi_joiner.pth",
    "Vedika/vedika/data/sandhi_split.pth",
    "Vedika/vedika/data/cleaned_metres.json",
]

for relative_path in source_paths:
    src = os.path.join(repo_path, relative_path)
    dst = os.path.join(data_dir, os.path.basename(relative_path))
    shutil.copy(src, dst)
    print(f"Copied {src} → {dst}")
