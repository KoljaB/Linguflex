import os
import sys
import subprocess
import platform
import re

# Environment
requirements_file_path = "conda_requirements.txt"
log_file_path = "conda_install_log.txt"
script_dir = os.getcwd()
conda_env_path = os.path.join(script_dir, "installer_files", "env")

def printl(message="", log_file=log_file_path, noprint=False):
    if not noprint:
        print(message)
    with open(log_file, "a", encoding='utf-8') as file:
        file.write(message + "\n")

def is_linux():
    return sys.platform.startswith("linux")

def is_windows():
    return sys.platform.startswith("win")

def is_macos():
    return sys.platform.startswith("darwin")

def is_x86_64():
    return platform.machine() == "x86_64"

def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    # Use the conda environment
    if environment:
        if is_windows():
            conda_bat_path = os.path.join(script_dir, "installer_files", "conda", "condabin", "conda.bat")
            cmd = f'"{conda_bat_path}" activate "{conda_env_path}" >nul && {cmd}'
        else:
            conda_sh_path = os.path.join(script_dir, "installer_files", "conda", "etc", "profile.d", "conda.sh")
            cmd = f'. "{conda_sh_path}" && conda activate "{conda_env_path}" && {cmd}'

    # Run shell commands
    printl(f"Running command {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    # Assert the command ran successfully
    if assert_success and result.returncode != 0:
        printl(f"Command '{cmd}' failed with exit status code '{str(result.returncode)}'.\n\nExiting now.\nTry running the start/update script again.")
        sys.exit(1)

    return result

def check_env():
    conda_prefix = os.environ.get('CONDA_PREFIX', '')
    if not conda_prefix:
        printl("This script must be run inside a conda environment.")
        sys.exit(1)
    if os.environ.get('CONDA_DEFAULT_ENV', '') == 'base':
        printl("Please create and activate a conda environment first.")
        sys.exit(1)

def get_user_choice(question, options_dict):
    printl()
    printl(question)
    printl()

    for key, value in options_dict.items():
        printl(f"{key}) {value}")

    printl()

    choice = input("Input> ").upper()
    while choice not in options_dict.keys():
        printl("Invalid choice. Please try again.")
        choice = input("Input> ").upper()

    return choice

def select_gpu():
    choice = get_user_choice(
        "What is your GPU?",
        {
            'A': 'NVIDIA',
            'B': 'AMD (Linux/MacOS only. Requires ROCm SDK 5.6 on Linux)',
            'C': 'Apple M Series',
            'D': 'Intel Arc (IPEX)',
            'N': 'None (I want to run models in CPU mode)'
        },
    )

    gpu_choice_to_name = {
        "A": "NVIDIA",
        "B": "AMD",
        "C": "APPLE",
        "D": "INTEL",
        "N": "NONE"
    }

    selected_gpu = gpu_choice_to_name[choice]
    return selected_gpu

def get_cuda_version():
    try:
        nvcc_output = subprocess.check_output("nvcc --version", shell=True).decode()
        match = re.search(r"release (\d+\.\d+)", nvcc_output)
        if match:
            cuda_version = match.group(1)
            printl(f"CUDA Toolkit version {cuda_version} detected.")
            return cuda_version
        else:
            return None
    except subprocess.CalledProcessError:
        return None

def get_install_pytorch_command(selected_gpu):
    TORCH_VERSION = "2.5.0"
    TORCHAUDIO_VERSION = "2.5.0"
    # TORCH_VERSION = "2.1.2"
    # TORCHAUDIO_VERSION = "2.1.2"
    install_pytorch = f"python -m pip install torch=={TORCH_VERSION} torchaudio=={TORCHAUDIO_VERSION} "
    if selected_gpu == "NVIDIA":
        cuda_version = get_cuda_version()
        if cuda_version is not None:
            if cuda_version.startswith('12'):
                cuda_ver = 'cu121'
            elif cuda_version.startswith('11'):
                cuda_ver = 'cu118'
            else:
                # If CUDA version is neither 11.x nor 12.x, default to cu121
                cuda_ver = 'cu121'
            index_url = f"https://download.pytorch.org/whl/{cuda_ver}"
            install_pytorch += f"--index-url {index_url}"
        else:
            # Ask the user
            printl("Could not detect CUDA version.")
            choice = input("Do you want to use CUDA 11.8 or 12.1? (Enter 11.8 or 12.1): ")
            while choice not in ['11.8', '12.1']:
                printl("Invalid choice. Please try again.")
                choice = input("Enter 11.8 or 12.1: ")
            if choice == '11.8':
                index_url = "https://download.pytorch.org/whl/cu118"
            else:
                index_url = "https://download.pytorch.org/whl/cu121"
            install_pytorch += f"--index-url {index_url}"
    elif selected_gpu == "AMD":
        install_pytorch += "--index-url https://download.pytorch.org/whl/rocm5.6"
    elif selected_gpu in ["APPLE", "NONE"]:
        install_pytorch += "--index-url https://download.pytorch.org/whl/cpu"
    elif selected_gpu == "INTEL":
        if is_linux():
            install_pytorch = "python -m pip install torch==2.1.0a0 torchaudio==2.1.0a0 intel-extension-for-pytorch==2.1.10+xpu --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/"
        else:
            install_pytorch = "python -m pip install torch==2.1.0a0 torchaudio==2.1.0a0 intel-extension-for-pytorch==2.1.10 --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/"

    return install_pytorch

def install_torch(selected_gpu):
    install_pytorch_cmd = get_install_pytorch_command(selected_gpu)
    printl(f"Installing PyTorch with command: {install_pytorch_cmd}")
    run_cmd(install_pytorch_cmd, assert_success=True)

def install_deepspeed():
    DEEPSPEED_VERSION = "0.11.2"
    if is_windows():
        cuda_version = get_cuda_version()
        if cuda_version is None:
            # Ask the user
            printl("Could not detect CUDA version.")
            choice = input("Do you have CUDA 11.8 or 12.1? (Enter 11.8 or 12.1): ")
            while choice not in ['11.8', '12.1']:
                printl("Invalid choice. Please try again.")
                choice = input("Enter 11.8 or 12.1: ")
            cuda_version = choice
        else:
            if cuda_version.startswith('12'):
                cuda_version = '12.1'
            elif cuda_version.startswith('11'):
                cuda_version = '11.8'
            else:
                # If cuda_version is higher than 12.1, set to 12.1
                cuda_version = '12.1'

        python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
        wheel_url = f"https://github.com/daswer123/deepspeed-windows-wheels/releases/download/11.2/deepspeed-{DEEPSPEED_VERSION}+cuda{cuda_version.replace('.', '')}-{python_version}-{python_version}-win_amd64.whl"

        printl(f"Installing DeepSpeed from wheel: {wheel_url}")
        run_cmd(f"python -m pip install {wheel_url}", assert_success=True)
    else:
        printl("Installing DeepSpeed using pip.")
        run_cmd("python -m pip install deepspeed", assert_success=True)

# def install_flash_attention():
#     if is_windows():
#         FLASH_ATTN_VERSION = "2.5.6"
#         python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
#         wheel_url = f"https://github.com/oobabooga/flash-attention/releases/download/v{FLASH_ATTN_VERSION}/flash_attn-{FLASH_ATTN_VERSION}+cu122torch2.1.2cxx11abiFALSE-{python_version}-{python_version}-win_amd64.whl"
#         printl(f"Installing Flash Attention from wheel: {wheel_url}")
#         run_cmd(f"python -m pip install {wheel_url}", assert_success=True)
#     else:
#         printl("Installing Flash Attention using pip.")
#         run_cmd("python -m pip install flash-attn", assert_success=True)

def install_transformers():
    printl("Installing transformers==4.38.2")
    run_cmd("python -m pip install transformers==4.38.2", assert_success=True)


def ask_exit(
        main_text,
        input_text="Do you want to try anyway? (yes/no): "
        ):
    printl(main_text)
    choice = input(input_text)

    # Check user's decision
    if choice.lower() not in ['yes', 'y']:
        printl("Installation aborted.")
        sys.exit()

def install_library(library):
    try:
       # Extract the base package name and extras (if any)
        base_package = library.split('[')[0]
        
        # Run pip install and capture the output and error
        printl(f"Installing library {base_package}")
        result = subprocess.run([sys.executable, "-m", "pip", "install", library], capture_output=True, text=True)

        # Check if the installation was successful or if the package is already installed
        if f"Requirement already satisfied: {base_package}" in result.stdout:
            printl(f"Already installed {library}")
            printl(f"  {result.stdout}", noprint=True)
            return True

        elif "Successfully installed" in result.stdout:
            printl(f"Successfully installed {library}")
            printl(f"  {result.stdout}", noprint=True)
            return True
        else:
            printl(f"  {result.stdout}", noprint=True)
            ask_exit(
                f"Failed to install {library}. Error: {result.stderr}",
                f"Do you want to continue installation without verified installation of {library}? (yes/no): "
            )
            return False

    except subprocess.CalledProcessError as e:
        ask_exit(
            f"Installation failed for {library}. Error: {e}",
            f"Do you want to continue installation without verified installation of {library}? (yes/no): "
        )
        return True

def install_libraries_from_requirements(file_path):
    try:
        with open(file_path, 'r') as file:
            libraries = file.readlines()

        for library in libraries:
            library = library.strip()
            if library and not library.startswith('#'):  # Skip empty lines and comments
                install_library(library)

    except FileNotFoundError:
        printl(f"The file {file_path} was not found. Please ensure it's in the correct path.")

def set_pip_version():
    printl("Setting pip version")
    
    # WE NEED pip 24.1 because latest fairseq==0.12.2 needed for rvc post processing does only support pip<24.1 currently
    # https://github.com/facebookresearch/fairseq/issues/5518
    run_cmd("python -m pip install \"pip<24.1\"", assert_success=True)



    #run_cmd("python -m pip install \"pip==24.0.0\"", assert_success=True)

    #run_cmd("python -m pip install --upgrade pip", assert_success=True)

def install_requirements():
    set_pip_version()

    path_to_git = os.path.join(script_dir, ".git")
    if not os.path.exists(path_to_git):
        git_creation_cmd = 'git init -b main && git remote add origin https://github.com/KoljaB/Linguflex && git fetch && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main && git reset --hard origin/main && git branch --set-upstream-to=origin/main'
        run_cmd(git_creation_cmd, environment=True, assert_success=True)
    else:
        printl(f"Git {path_to_git} already initialized")
    
    printl("Installing required libraries")
    install_libraries_from_requirements(requirements_file_path)


def download_models():
    try:
        subprocess.run(['python', 'download_models.py'])
    except subprocess.CalledProcessError as e:
        printl(f"Failed to download pre-trained models. Error: {e}")
        ask_exit("Do you want to continue without downloading pre-trained models? (yes/no): ")

def download_file(url, destination):
    import requests
    from tqdm import tqdm as tqdm_lib
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024

    progress_bar = tqdm_lib(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

def download_xtts_base_model(model_name="v2.0.2", local_models_path="models/xtts"):

    # Creating a unique folder for each model version
    if local_models_path and len(local_models_path) > 0:
        model_folder = os.path.join(local_models_path, f'{model_name}')
        print(f"Local models path: \"{model_folder}\"")
    else:
        model_folder = os.path.join(os.getcwd(), 'models', f'{model_name}')
        print(f"Checking for models within application directory: \"{model_folder}\"")

    os.makedirs(model_folder, exist_ok=True)

    files = {
        "config.json": f"https://huggingface.co/coqui/XTTS-v2/raw/{model_name}/config.json",
        "model.pth": f"https://huggingface.co/coqui/XTTS-v2/resolve/{model_name}/model.pth?download=true",
        "vocab.json": f"https://huggingface.co/coqui/XTTS-v2/raw/{model_name}/vocab.json",
        "speakers_xtts.pth": f"https://huggingface.co/coqui/XTTS-v2/resolve/{model_name}/speakers_xtts.pth",
    }

    for file_name, url in files.items():
        file_path = os.path.join(model_folder, file_name)
        if not os.path.exists(file_path):
            print(f"Downloading {file_name} to {file_path}...")
            download_file(url, file_path)
            print(f"{file_name} downloaded successfully.")
        else:
            print(f"{file_name} exists in {file_path} (no download).")

    return model_folder


def launch_linguflex():
    run_cmd("python -m lingu.core.run", assert_success=True)


if __name__ == "__main__":
    check_env()
    selected_gpu = select_gpu()
    # install_deepspeed()
    install_requirements()
    install_torch(selected_gpu)
    # install_flash_attention()
    #install_transformers()
    download_models()
    download_xtts_base_model()

    if not is_linux():
        launch_linguflex()
