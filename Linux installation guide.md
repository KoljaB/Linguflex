# Linux Installation Guide

(tested on: Ubuntu 24.04.1 LTS codename "Noble.")

## Install Linguflex Core

### 1. Create a Virtual Environment

```bash
git clone -b linux https://github.com/KoljaB/Linguflex.git
cd Linguflex
chmod +x linux_install.sh
./linux_install.sh
```

- **Note:** Remember the command displayed after running `linux_install.sh` about how to start the virtual environment.

### 2. Restart the Terminal

- Close the terminal and open it again.

### 3. Activate the Virtual Environment

- Activate the virtual environment by entering the command you noted earlier. For example:

    ```bash
    conda activate /home/username/Dev/Linguflex/Linguflex/installer_files/env
    ```

### 4. Navigate to the Linguflex Folder

```bash
cd /path/to/Dev/Linguflex/Linguflex
```

### 5. Install Dependencies

```bash
python conda_install.py
```

### 6. List Audio Devices

```bash
python show_devices.py
```

- This command lists all audio input and output devices.

#### If You Encounter GLIBCXX_3.4.32 Errors:

**Rename or Remove the Outdated `libstdc++.so.6`**

- Rename the `libstdc++.so.6` file in your virtual environment's `lib` directory to prevent it from being used:

    ```bash
    mv /home/username/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6 \
    /home/username/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6.bak
    ```

### 7. Configure Audio Devices

- Select an `input_device_index` for microphone recording and an `output_device_index` for TTS playback from the list displayed by `python show_devices.py`.

- Open `lingu/settings.yaml` and update the following:

    - Set `listen/input_device_index` to your selected `input_device_index`.
    - Set `speech/output_device_index` to your selected `output_device_index`.

**Tips:**

- **Input Device Index:**
  - Look for the name of your main microphone in the list.
- **Output Device Index:**
  - Look for devices where **Max Output Channels** > 0.
  - For speakers/headphones, look for names like **HDA Intel PCH: Analog**.
  - For HDMI audio, look for names containing **HDMI**.

*Note:* Selecting suitable input and output devices can be tricky. If unsure, you can leave them at `-1`, and the system will attempt to find suitable ones. However, it's usually better to set them yourself.

### 8. [Optional] Provide API Keys

- Open `_set_env_linux.sh` and enter any API keys you wish to provide. This step is optional if you do not plan to use them.

### 9. Start Linguflex

```bash
sudo bash -c "source /home/$USER/Dev/Linguflex/Linguflex/installer_files/conda/etc/profile.d/conda.sh && \
conda activate /home/$USER/Dev/Linguflex/Linguflex/installer_files/env && \
source /home/username/Dev/Linguflex/Linguflex/_set_env_linux.sh && \
python -m lingu.core.run"
```

### 10. Stop Linguflex

```bash
sudo pkill -9 -f "python -m lingu.core.run"
```

## Prerequisites

For local inference with Linguflex, you need a local LLM provider. Please install **one** of the following:

### Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### LM Studio

- Download the AppImage from [LM Studio](https://lmstudio.ai/).

- Change the filename to match the downloaded file and run:

    ```bash
    cd /path/to/directory
    chmod u+x LM_Studio-0.3.5.AppImage
    ./LM_Studio-0.3.5.AppImage
    ```

### VLLM

```bash
pip install vllm
```

You can also specify OpenAI as your main LLM provider or use openrouter.