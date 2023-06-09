# Linguflex Installation Guide

Please follow these steps carefully to ensure a successful installation of Linguflex.

## Step 1: Set Up OpenAI API Key

1. Create an account at [OpenAI Signup Page](https://platform.openai.com/signup).
2. Once logged in, click on your name at the top right and select "View API keys".
3. Click on "Create new secret key" and generate a new API Key.

## Step 2: Install Python

1. Visit the [Python 3.9.9 Installation Page](https://www.python.org/downloads/release/python-399/).
2. Scroll to the bottom and select "Windows installer (64-bit)". This is applicable for most systems.

## Step 3: Download Linguflex

1. Download [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip).
2. Extract the ZIP file to your desired location.

## Step 4: [Optional] Install PyTorch with CUDA Support

> Note: This step is optional, but it enables faster language recognition by using your graphics card. It only works with [specific Nvidia graphics cards](https://developer.nvidia.com/cuda-gpus).

1. Install [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive).
2. Open the command prompt and run the following command:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Step 5: Install Linguflex

1. Open the command prompt.
2. Navigate to the folder you created in Step 3.
3. Execute the following command:
   ```bash
   pip install -r requirements.txt
   ```

## Step 6: Launch Linguflex

Run the following command in your command prompt:

```bash
python linguflex
```

## Post-Installation: Microphone Calibration

After successfully launching Linguflex, it would be beneficial to calibrate your microphone:

1. Set `debug_show_volume = True` in the `config.txt` file under the `[microphone_recorder]` section.
2. Start Linguflex and observe the volume levels in the output.
3. Write appropriate values for `volume_start_recording` and `volume_stop_recording` in the `config.txt` file.
