# Linguflex Installation Guide

Welcome to the Linguflex installation guide. Try to keep close to the recommended environment to enhance the likelihood of a successful installation and smooth operation. This software was developed and tested under Windows. Although primarily developed and tested for Windows, compatibility with other platforms might be possible but remains unverified. Any insights on Linux or Mac installation or operational challenges are greatly welcomed.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Windows Installation](#windows-installation)
   - [For Windows Users](#for-windows-users)
   - [For Other Platforms](#for-other-platforms)
3. [Adjust Settings](#adjust-settings)
4. [Environment Variables](#environment-variables)
   - [Temporary Setting](#temporary-setting)
   - [Permanent Setting](#permanent-setting)
5. [Starting the Application](#starting-the-application)

## Prerequisites
Before you begin, ensure you have the following:
- Operating System: Windows 10 or 11 (Linux may work but requires additional experience)
- Graphics Card: Nvidia (recommended for full feature access)
- Python Version: [3.10.9](https://www.python.org/downloads/release/python-3109/)
  <details>
  <summary>Why exactly this python version?</summary>

    - Because we use RVC Postprocessing.
    - The code to do this is based on the realtime processing of [RVC WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) project. The [requirements.txt](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/blob/main/requirements.txt) only works with python <3.11 - if you find a way to install all dependencies on 3.11 or 3.12 let me know.
  </details> 
- [NVIDIA CUDA Toolkit 12.X](https://developer.nvidia.com/cuda-downloads)
  or [NVIDIA CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive)
- [NVIDIA cuDNN for CUDA 12.x](https://developer.nvidia.com/cudnn-downloads)
  or [NVIDIA cuDNN 8.7.0 for CUDA 11.x](https://developer.nvidia.com/rdp/cudnn-archive)
  [🎥 Setup Tutorial for CUDA + cuDNN](https://www.youtube.com/watch?v=OEFKlRSd8Ic)
- [ffmpeg](https://ffmpeg.org/download.html)  
  [🎥 Setup Tutorial for ffmpeg](https://www.youtube.com/watch?v=jZLqNocSQDM)
- If you want to start with OpenAI-Client, set your OpenAI API key:  
  Windows: `setx OPENAI_API_KEY "your-api-key-here"`  
  macOS and Linux: `export OPENAI_API_KEY='your-api-key-here'`

Additional components that may be required:
- eSpeak NG (possibly needed for certain text-to-speech functionalities)
- Visual Studio Build Tools (may be necessary for compiling some libraries)

If you've encountered any issues with the installation process, here are a few ways you can contribute:

- Submit a Pull Request (PR) to the GitHub repository with specific changes or additions to the installation documentation. This direct approach also gets your name listed among the project contributors.
- Alternatively, submit an [Issue on GitHub](https://github.com/KoljaB/Linguflex/issues/new/choose), send an [Email](mailto:kolja.beigel@web.de), or discuss in our [Discord channel](https://discord.gg/f556hqRjpv).

Please share your feedback to make Linguflex more user-friendly and accessible. By contributing to the documentation, you help new users have a smooth start.

## Windows Installation

### For Windows Users
#### 1. Clone the Project:
   ```bash
   git clone https://github.com/KoljaB/Linguflex.git
   cd Linguflex
   ```

#### 2. Installation Process:
   - **If Python 3.10.9 is your main Python environment:**
     - Proceed directly to running the installation script.

   - **If Python 3.10.9 is not your main Python environment:**
     - Open `_install_win.bat`.
     - Enter the path to Python 3.10.9 `.exe` on the second line, e.g.,
       ```bash
       set PYTHON_EXE=D:\Programme\miniconda3\envs\textgen\python.exe
       ```
     - Save the file.

   - **Run the Installation Script:**
     ```bash
     _install_win.bat
     ```

### For Other Platforms
(Linux, Mac, etc. - Note: These require additional expertise)
- Install the requirements and dependencies:
  ```bash
  pip install -r requirements.txt
  pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118
  pip install deepspeed
  pip install llama-cpp-python
  python download_models.py   
  ```

## Adjust Settings
Edit the `lingu/settings.yaml` file to tailor Linguflex to your setup requirements. For the mail module to function properly, you must configure the IMAP server, username, and password in this settings file.  

To use the project's default language model, you need to set the OPENAI_API_KEY. Alternatively, to switch to a local language model, adjust the use_local_llm parameter in the local_llm section of settings.yaml to true.

## Environment Variables
### Setting Environment Variables:

#### Temporary Setting (Session-only):
For temporary usage (lasts until the Command Prompt session is closed):
```cmd
set OPENAI_API_KEY=your_openai_api_key_here
```

#### Permanent Setting:
For permanent usage (persists across sessions and reboots):
```cmd
setx OPENAI_API_KEY "your_openai_api_key_here"
```

Required Variables:
- `OPENAI_API_KEY` (for GPT API)
- `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` (for Azure TTS)
- `ELEVENLABS_API_KEY` (for Elevenlabs TTS)
- `GOOGLE_API_KEY` (for Music Playout)
- `OPENWEATHERMAP_API_KEY` (for Weather module)

## Starting the Application
Run the application using:
```bash
python -m lingu.core.run
```
Or execute `run.bat`.
