# Linguflex Installation Guide

## Step 1: Set up OpenAI API Key
*allows access to the AI API*

1. Create an account on the [OpenAI signup page](https://platform.openai.com/signup).
2. Click on the name at the top right and select "View API keys".
3. Click on "Create new secret key" and generate a new API key.

## Step 2: Install Python
*provides the software platform on which Linguflex was built*

1. Visit [Python 3.9.9 installation page](https://www.python.org/downloads/release/python-399/) 
   (Python 3.9.9, as Whisper was trained and tested on this version)
2. Scroll down and select "Windows installer (64-bit)". This applies to most systems.

## Step 3: Install FFmpeg
*provides the library needed for Whisper's speech recognition*

1. Download the [ZIP file of the latest FFmpeg version](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) from https://www.gyan.dev/ffmpeg/builds/.
2. Unpack this file with any archive program such as 7zip or Winrar.
3. Rename the unpacked folder to 'ffmpeg' and move it to the root folder of your C: drive.
4. Open the command prompt with administrator rights and execute the following command:
   ```bash
   setx /m PATH "C:\ffmpeg\bin;%PATH%"
   ```
5. Restart your computer. You can verify the installation by running the command:
   ```bash
   ffmpeg -version
   ```

## Step 4: [Optional] Install PyTorch with CUDA Support
*allows faster (GPU-based) speech recognition by Whisper*

> Note: This step is optional, but highly recommended if a graphics card from [this list](https://developer.nvidia.com/cuda-gpus) is present 

1. Install [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive).
2. Open command prompt and run the following command:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Step 5: Download Linguflex

1. Download [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip).
2. Extract ZIP file into desired Linguflex installation folder.

## Step 6: Install Linguflex

1. Open command prompt.
2. Navigate to the installation folder from step 5.2.
3. Run the following command:
   ```bash
   pip install -r requirements.txt
   ```
4. (optional but recommended) Upgrade tiktoken.
   ```bash
   pip install --upgrade tiktoken
   ```
5. Open config.txt or start_linguflex.bat file in a text editor
   config.txt: enter your OpenAI API Key into parameter api_key of section [openai_generator] 
   start_linguflex.bat: enter your OpenAI API Key at the line set OPENAI_API_KEY=

## Step 7: Launch Linguflex

The system is now ready to start the core version of Linguflex.

To do this, run the following batch file in the Linguflex installation folder:

```bash
start_linguflex
```

Alternatively: python linguflex.py
   
## After Installation

### Set up Modules

After installing the basic version, the core functionality can be expanded by adding modules.

Please look into the following documents to get started:

[Module Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md)

[Configuration Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md)

### Calibrate Microphone

After successfully starting Linguflex, it is beneficial to calibrate the microphone:

1. Set `debug_show_volume = True` in the `config.txt` file under the `[microphone_recorder]` section.
2. Start Linguflex and observe the volume levels in the output.
3. Write suitable values for `volume_start_recording` and `volume_stop_recording` into the `config.txt` file.

### Commissioning of Remaining Modules

The basic version of Linguflex can now be started.  
Afterwards, modules can be added in the configuration file to extend the functionality of Linguflex.

For this, select a module from the list in the [modules] section of the configuration file and uncomment it. Follow the description in the [Module Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md) and the [Configuration Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md) to set up the module.
