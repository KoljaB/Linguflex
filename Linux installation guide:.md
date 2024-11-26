# Linux Installation Guide

## Install Linguflex Core 

- Create Virtual Environment 
    ```bash
    git clone -b linux https://github.com/KoljaB/Linguflex.git
    cd Linguflex
    chmod +x linux_install.sh
    ./linux_install.sh
    ```

- remember the command that gets displayed now about how to start the venv

- restart the terminal (close it and open it again)

- activate venv by entering the remembered command
  like:
    conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env 

- move to Linguflex folder, example:
    cd Dev
    cd Linguflex
    cd Linguflex

- execute
    python conda_install.py

- execute
    python show_devices.py

    to list all audio input and output devices

    If you get errors related to `GLIBCXX_3.4.32`:
    
        **Rename or Remove the Outdated `libstdc++.so.6`**

        Rename the `libstdc++.so.6` file in your virtual environment's `lib` directory to prevent it from being used:

        ```bash
        mv /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6 /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6.bak
        ```   

- select an input_device_index for microphone recording and an output_device_index for TTS playout from the list displayed by python show_devices.py

- open lingu/settings.yaml

    - write the selected input_device_index into listen/input_device_index
    - write the selected output_device_index into speech/output_device_index

    The selection of suitable input and output devices can be a bit tricky. If you are unsure you can leave them at -1 and the system will try to finde suitable ones. In most cases it's better to set them for yourselfs though.

    Tipps:
    For input_device_index look for the name of your main microphone in the list.

    For output_device_index:
    - Look for devices where **Max Output Channels** > 0.
    - For speakers/headphones, look for names like `HDA Intel PCH: Analog`.
    - For HDMI audio, look for names with `HDMI`.


- [optional] open _set_env_linux.sh and enter the api keys you want to provide (you don't need to provide anything if you don't want to use it)

- start Linguflex

    sudo bash -c "source /home/lon/Dev/Linguflex/Linguflex/installer_files/conda/etc/profile.d/conda.sh && conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env && source /home/lon/Dev/Linguflex/Linguflex/_set_env_linux.sh && python -m lingu.core.run"

- kill Linguflex
    sudo pkill -9 -f "python -m lingu.core.run"



## Prerequisites:

For local inference which is what you all want to do with Linguflex you will need a local LLM provider.

Please install either:

### Ollama

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

### LM Studio
    - load the AppImage:
    https://lmstudio.ai/


    Change filename to the actual downloaded filename:
    ```bash
    cd /path/to/directory
    chmod u+x LM_Studio-0.3.5.AppImage
    ./LM_Studio-0.3.5.AppImage
    ```

### VLLM

    ```bash
    pip install vllm
    ```
