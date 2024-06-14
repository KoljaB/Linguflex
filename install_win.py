import subprocess
import platform
import sys
import re
import os

always_clear_pip = False
always_download_models = False
requirements_file_path = "requirements.txt"
log_file_path = "log_install_python.txt"

with open(log_file_path, 'w', encoding='utf-8') as log_file:
    log_file.write("Starting installation script...\n")


def printl(message, log_file=log_file_path, noprint=False):
    if not noprint:
        print(message)
    with open(log_file, "a", encoding='utf-8') as file:
        file.write(message + "\n")


def check_python_version():
    if sys.version_info[:3] != (3, 10, 9):
        ask_exit(
            "This script requires Python 3.10.9.\n"
            "Your version: " + ".".join(map(str, sys.version_info[:3]))+ "\n",
            "Do you want to proceed anyway? (yes/no): "
        )
    else:
        printl("Python version 3.10.9 detected.")

    return sys.version_info[:3]


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


def ask(
        main_text,
        input_text="Do you want to try anyway? (yes/no): "
        ):
    printl(main_text)
    choice = input(input_text)
    return choice.lower() in ['yes', 'y']


def check_platform():
    printl("Checking platform...")

    # Check if the current platform is Windows
    if platform.system() != "Windows":
        # Display a warning message if not on Windows
        ask_exit(
            "Warning: This installation script is designed for Windows platforms.",
            "Do you want to proceed despite being on a non-Windows platform? (yes/no): "
        )
    else:
        printl("  Windows platform detected.")


def check_cuda():
    printl("Checking CUDA Toolkit...")

    try:
        # Execute nvcc to get CUDA version
        nvcc_output = subprocess.check_output("nvcc --version", shell=True).decode()

        # Use regular expression to extract version number
        match = re.search(r"release (\d+\.\d+)", nvcc_output)
        if match:
            cuda_version = match.group(1)
            if cuda_version == "11.8":
                printl(f"  CUDA Toolkit version {cuda_version} detected.")
            else:
                ask_exit(
                    f"CUDA Toolkit version {cuda_version} detected.\n"
                    "- Version 11.8 is recommended.\n"
                    "  https://developer.nvidia.com/cuda-11-8-0-download-archive",
                    "Do you want to continue with a different version of CUDA? (yes/no): "
                )
            return cuda_version
        else:
            ask_exit(
                "CUDA Toolkit version 11.8 could not be detected.\n"
                "- Version 11.8 is strongly recommended.\n"
                "  https://developer.nvidia.com/cuda-11-8-0-download-archive",
                "Do you want to proceed despite CUDA 11.8 was not detected? (yes/no): "
            )
            return "11.8"

    except subprocess.CalledProcessError:
        ask_exit(
            "CUDA Toolkit version 11.8 could not be detected.\n"
            "- Version 11.8 is strongly recommended.\n"
            "  https://developer.nvidia.com/cuda-11-8-0-download-archive",
            "Do you want to proceed despite CUDA 11.8 was not detected? (yes/no): "
        )
        return "11.8"


def check_cudnn():
    printl("Checking cuDNN...")

    # Typical paths where cuDNN might be installed
    cudnn_paths = [
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\bin",
        r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8\include",
        r"C:\tools\cuda\bin",
        r"C:\tools\cuda\include"
    ]

    cudnn_h_found = False
    cudnn_dll_found = False

    # Check if cuDNN files exist in the typical paths
    for path in cudnn_paths:
        if os.path.exists(os.path.join(path, "cudnn.h")):
            cudnn_h_found = True
        # Check for the existence of the cuDNN library file (dll)
        # The file name can vary based on the cuDNN version
        # Here we are checking for version 7 as an example
        if any(os.path.exists(os.path.join(path, f)) for f in ["cudnn64_7.dll", "cudnn64_8.dll"]):
            cudnn_dll_found = True

    if cudnn_h_found and cudnn_dll_found:
        printl("  cuDNN installation detected.")
    else:
        ask_exit(
            "cuDNN installation not found.\n"
            "- Version 8.7.0 for CUDA 11.8 is recommended.\n"
            "  https://developer.nvidia.com/rdp/cudnn-archive",
            "Do you want to despite cuDNN installation was not detected? (yes/no): "
        )


def check_ffmpeg():
    printl("Checking FFmpeg...")

    try:
        # Execute ffmpeg to check its presence
        subprocess.check_output("ffmpeg -version", shell=True)
        printl("  FFmpeg installation detected.")
    except subprocess.CalledProcessError:
        ask_exit(
            "FFmpeg not found. It is required for video processing.\n"
            "Please install FFmpeg.",
            "Do you want to continue without FFmpeg? (yes/no): "
        )


def install_library(library):
    try:
        # Run pip install and capture the output and error
        result = subprocess.run([sys.executable, "-m", "pip", "install", library], capture_output=True, text=True)

        # Check if the installation was successful or if the package is already installed
        if f"Requirement already satisfied: {library}" in result.stdout:
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


def purge_pip_cache():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "cache", "purge"])
        printl("Pip cache cleared successfully.")
    except subprocess.CalledProcessError as e:
        printl(f"Failed to clear pip cache. Error: {e}")


def is_greater_version(v1, v2):
    # Split version numbers into parts and convert to integers
    parts1 = [int(part) for part in v1.split('.')]
    parts2 = [int(part) for part in v2.split('.')]

    # Compare version number parts
    return parts1 > parts2


def install_deepspeed(deepspeed_version, cuda_version, python_version):
    # Mapping of Deepspeed version, CUDA version, and Python version to wheel URL

    wheel_urls = {
        ("0.11.2", "11.8", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/11.2/deepspeed-0.11.2+cuda118-cp310-cp310-win_amd64.whl",
        ("0.11.2", "12.1", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/11.2/deepspeed-0.11.2+cuda121-cp310-cp310-win_amd64.whl",
        ("0.11.2", "11.8", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/11.2/deepspeed-0.11.2+cuda118-cp311-cp311-win_amd64.whl",
        ("0.11.2", "12.1", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/11.2/deepspeed-0.11.2+cuda121-cp311-cp311-win_amd64.whl",
        ("0.12.6", "11.8", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/12.6/deepspeed-0.12.6+cu118-cp310-cp310-win_amd64.whl",
        ("0.12.6", "12.1", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/12.6/deepspeed-0.12.6+cu121-cp310-cp310-win_amd64.whl",
        ("0.12.6", "11.8", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/12.6/deepspeed-0.12.6+cu118-cp311-cp311-win_amd64.whl",
        ("0.12.6", "12.1", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/12.6/deepspeed-0.12.6+cu121-cp311-cp311-win_amd64.whl",
        ("0.13.1", "11.8", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/13.1/deepspeed-0.13.1+cu118-cp310-cp310-win_amd64.whl",
        ("0.13.1", "12.1", (3, 10)): "https://github.com/daswer123/deepspeed-windows/releases/download/13.1/deepspeed-0.13.1+cu121-cp310-cp310-win_amd64.whl",
        ("0.13.1", "11.8", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/13.1/deepspeed-0.13.1+cu118-cp311-cp311-win_amd64.whl",
        ("0.13.1", "12.1", (3, 11)): "https://github.com/daswer123/deepspeed-windows/releases/download/13.1/deepspeed-0.13.1+cu121-cp311-cp311-win_amd64.whl"
    }

    if is_greater_version(cuda_version, "12.1"):
        cuda_version = "12.1"

    # Constructing the key for the mapping
    key = (deepspeed_version, cuda_version, (python_version[0], python_version[1]))

    # Get the wheel URL from the mapping
    wheel_url = wheel_urls.get(key)
    if wheel_url:
        # Install the wheel using pip
        return install_library(wheel_url)
    else:
        printl(f"No matching wheel found for Deepspeed version {deepspeed_version}, CUDA version {cuda_version}, Python version {python_version[0]}.{python_version[1]}")
        printl("Trying to install deepspeed with pip ...")
        return install_library("deepspeed")


def install_llama_cpp_python(cuda_version):
    printl("Installing llama-cpp-python...")

    try:
        # Set environment variables if necessary
        os.environ['CMAKE_ARGS'] = '-DLLAMA_CUBLAS=on'
        os.environ['FORCE_CMAKE'] = '1'

        # Perform installation with pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python", "--force-reinstall", "--upgrade", "--no-cache-dir", "--verbose"])

        printl("Successfully installed llama-cpp-python.")
        return True

    except subprocess.CalledProcessError as e:
        printl(f"Failed to install llama-cpp-python. Error: {e}")
        printl(f"Linguflex can run without llama-cpp-python. You can't use llama.cpp as model_provider in the local_llm section of the settings.yaml file. If you want to use local llms please select ollama as provider.")
        printl(f"You may need to copy MSBuildExtensions files for CUDA {cuda_version}.")
        printl(f"Copy all four MSBuildExtensions files from:\n"
                f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{cuda_version}\\extras\\visual_studio_integration\\MSBuildExtensions\n"
                f"to\n"
                f"C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\MSBuild\\Microsoft\\VC\\v170\\BuildCustomizations\n"
                f"before restarting the installation script or manually executing the following command:\n"
                f"pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir --verbose")
        ask_exit("Do you want to continue without a verified installation of llama-cpp-python? (yes/no): ")
        return False


def install_pytorch_torchaudio(cuda_version):
    printl("Installing PyTorch and Torchaudio...")

    torch_wheels = {
        "11.8": "torch==2.2.2+cu118 torchaudio==2.2.2+cu118",
        "12.1": "torch==2.2.2+cu121 torchaudio==2.2.2+cu121",
    }

    if is_greater_version(cuda_version, "12.1"):
        cuda_version = "12.1"

    torch_wheel = torch_wheels.get(cuda_version)

    if torch_wheel:
        # Install the wheel using pip
        packages = torch_wheel.split()
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *packages, "--index-url", "https://download.pytorch.org/whl/cu" + cuda_version.replace('.', '')])
            # subprocess.check_call([sys.executable, "-m", "pip", "install", torch_wheel, "--index-url", "https://download.pytorch.org/whl/cu" + cuda_version.replace('.', '')])
            printl(f"Successfully installed PyTorch and Torchaudio for CUDA {cuda_version}.")
        except subprocess.CalledProcessError as e:
            printl(f"Failed to install PyTorch and Torchaudio. Error: {e}")
            ask_exit(
                f"Failed to install PyTorch and Torchaudio. Error: {e}",
                "Do you want to continue without a verified installation of PyTorch and Torchaudio? (yes/no): ")
    else:
        ask_exit(
            f"No matching wheels found for CUDA version {cuda_version}.",
            "Do you want to continue without a verified installation of PyTorch and Torchaudio? (yes/no): ")


def detect_vram():
    import pynvml

    pynvml.nvmlInit()
    device_count = pynvml.nvmlDeviceGetCount()
    vram_values = []
    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        vram_mb = info.total / 1024**2
        vram_values.append(vram_mb)
        print(f"GPU: {i}, VRAM: {vram_mb}MB")
    pynvml.nvmlShutdown()

    if vram_values:
        return max(vram_values)
    else:
        return 0


def download_models():
    try:
        subprocess.run(['python', 'download_models.py'])
    except subprocess.CalledProcessError as e:
        printl(f"Failed to download pre-trained models. Error: {e}")
        ask_exit("Do you want to continue without downloading pre-trained models? (yes/no): ")


if __name__ == "__main__":

    perform_download = always_download_models or \
        ask("Do you want to download pre-trained llm (OpenHermes-2.5-Mistral-7B-GGUF), xtts and rvc models (recommended for tts rvc post processing)?",
            "Please enter yes or no: ")

    clear_pip = always_clear_pip or \
        ask("Do you want to clear the pip cache? This can resolve some installation issues.", "Please enter yes or no: ")

    printl("\nChecking system requirements ...")
    python_version = check_python_version()
    check_platform()
    cuda_version = check_cuda()
    check_cudnn()
    check_ffmpeg()
    printl("System requirements check passed.\n")

    if clear_pip:
        purge_pip_cache()

    printl("\nInstalling required libraries ...")
    install_libraries_from_requirements(requirements_file_path)
    printl("\nInstalling torch with CUDA ...")
    install_pytorch_torchaudio(cuda_version)
    printl("\nInstalling required deepspeed ...")
    if not install_deepspeed("0.11.2", cuda_version, python_version):
        import yaml
        file_path = 'lingu/settings.yaml'
        # Load the YAML file
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        # Modify the 'coqui_use_deepspeed' setting under 'speech'
        if 'speech' in data and 'coqui_use_deepspeed' in data['speech']:
            data['speech']['coqui_use_deepspeed'] = False

        # Write the modified data back to the YAML file
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False)

    printl("\nInstalling required llama.cpp ...")    
    install_llama_cpp_python(cuda_version)
        
    printl("\nSetting numpy version ...")
    install_library("numpy==1.23.5")

    if perform_download:
        download_models()

    # vram_mb = detect_vram()
