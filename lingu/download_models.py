"""
Python script to download the models from Huggingface's model hub.
"""

from tqdm import tqdm
import requests
import os


local_hubert_path = "models/rvc/assets/hubert"
local_trained_path = "models/rvc/models"

hf_hubert_url = "https://huggingface.co/KoljaB/RVC_Assets/resolve/main"
hubert_base_file = "hubert_base.pt"
hubert_input_file = "hubert_inputs.pth"

hf_trained_url = "https://huggingface.co/KoljaB/RVC_Models/resolve/main"
rvc_models = ["Lasinya", "Samantha"]

hf_xtts_url = "https://huggingface.co/KoljaB/XTTS_Models/"
xtts_models = ["Lasinya", "Samantha"]

xtts_files = ["config.json", "model.pth", "speakers_xtts.pth", "vocab.json"]


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_directories():
    create_directory("models")
    create_directory("models/rvc")
    create_directory("models/rvc/assets")
    create_directory("models/rvc/models")
    create_directory("models/xtts")

    create_directory(local_hubert_path)
    create_directory(local_trained_path)


def download_file(url, filename):
    if os.path.exists(filename):
        print(f"File {filename} already exists.")
        return

    print(f"Downloading {url} to {filename}...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)


create_directories()

# download hubert (rvc base model) files
download_file(
    os.path.join(hf_hubert_url, hubert_base_file),
    os.path.join(local_hubert_path, hubert_base_file))
download_file(
    os.path.join(hf_hubert_url, hubert_input_file),
    os.path.join(local_hubert_path, hubert_input_file))


# download rvc trained model files
for model in rvc_models:
    download_file(
        os.path.join(hf_trained_url, f"{model}.pth"),
        os.path.join(local_trained_path, f"{model}.pth"))
    download_file(
        os.path.join(hf_trained_url, f"{model}.index"),
        os.path.join(local_trained_path, f"{model}.index"))


# download xtts trained model files
for model in xtts_models:
    xtts_path = hf_xtts_url + model + "/resolve/main"
    local_path = os.path.join("models/xtts", model)

    for file in xtts_files:
        download_file(
            os.path.join(xtts_path, file),
            os.path.join(local_path, file))



