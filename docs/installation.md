
# Installation Guide

This guide will help you set up your environment for the project. Please follow the steps carefully.

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

1. **Clone the project:**
   ```bash
   git clone -b lingu-2.0-preview https://github.com/KoljaB/Linguflex.git
   cd Linguflex
   ```

2. **Installation:**

   For windows:  

   ```bash
   _install_win.bat
   ```

   For other platforms (not recommended, esp Mac OS will prob not work):  
   ```bash
   pip install -r requirements.txt
   pip install torch==2.1.2+cu118 torchaudio==2.1.2+cu118 --index-url https://download.pytorch.org/whl/cu118
   pip install deepspeed
   pip install llama-cpp-python
   python download_models.py
   ```

3. **Adjust settings:**
   - adjust lingu/settings.yaml to configure linguflex to your environment
     - in mail section enter your mail server settings
   - setup the needed environment keys
     - OPENAI_API_KEY to use GPT API for answers
     - AZURE_SPEECH_KEY, AZURE_SPEECH_REGION to use Azure TTS
     - ELEVENLABS_API_KEY to use Elevenlabs TTS
     - GOOGLE_API_KEY to use Music Playout
     - OPENWEATHERMAP_API_KEY to use Weather module

4. **Start linguflex:**
   - start run.bat or type:
      ```bash
      python -m lingu.core.run
      ```
