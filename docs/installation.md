
# Linguflex Installation Guide

Welcome to the linguflex installation guide that helps you set up your environment for our project.  

Adhering closely to the recommended setup will greatly enhance the likelihood of a successful and smooth operation.

## Prerequisites
- Windows 10 or 11  
  (Linux may work but will probably require some experience installing complex projects)
- Nvidia Graphics Card recommended  
  (otherwise you might be restricted to only using APIs for LLM and TTS)
- Python 3.10.9  
  https://www.python.org/downloads/release/python-3109/
- NVIDIA CUDA Toolkit installed (11.8 STRONGLY recommended)  
  https://developer.nvidia.com/cuda-11-8-0-download-archive
- NVIDIA cuDNN installed (8.7.0 for CUDA 11.x recommended)  
  https://developer.nvidia.com/rdp/cudnn-archive
- ffmpeg installed  
  https://ffmpeg.org/download.html

## Windows-Installation

1. **Clone the project**:

   ```bash
   git clone -b lingu-2.0-preview https://github.com/KoljaB/Linguflex.git
   cd Linguflex
   ```

2. **Installation Process**:

   For windows run the batch file:
   ```bash
   _install_win.bat
   ```
   For other platforms (Linux, Mac, etc., which are less recommended):
   ```bash
   pip install -r requirements.txt
   pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118
   pip install deepspeed
   pip install llama-cpp-python
   python download_models.py   
   ```

3. **Adjust settings**:

   - Modify `lingu/settings.yaml` to suit your setup.
   - Set the required environment variables:
     - `OPENAI_API_KEY` for GPT API usage.
     - `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION` for Azure TTS.
     - `ELEVENLABS_API_KEY` for Elevenlabs TTS.
     - `GOOGLE_API_KEY` for Music Playout.
     - `OPENWEATHERMAP_API_KEY` for the Weather module.

4. **Starting the Application**:

   Either run `run.bat` or use the command:
   ```bash
   python -m lingu.core.run
