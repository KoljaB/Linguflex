Linux installation guide:
- Install ollama
  (I am unsure if this maybe gets automatically installed by open interpreter or so)

- Execute:
    ```bash
    chmod +x linux_create_venv.sh
    ./linux_create_venv.sh
    ```
- remember the command that gets displayed now about how to start the venv
- Execute:
    ```bash
    conda init bash
    ```
- restart terminal
- activate venv by entering the remembered command
  like:
    conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env 

- Execute:
    ```bash
    python conda_install.py
    ```
- follow the instructions





- find conda.sh:
    ```bash
    find ~/ -name conda.sh
    ```

- get conda env:
    ```bash
    conda info --envs
    ```

- start with:
    (replace path to conda.sh with result from find, replace activate env with your env)
    ```bash
    
    conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env 
    cd Dev/Linguflex/Linguflex
    sudo bash -c "source /home/lon/Dev/Linguflex/Linguflex/installer_files/conda/etc/profile.d/conda.sh && conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env && source /home/lon/Dev/Linguflex/_set_env_linux.sh && python -m lingu.core.run"
    sudo pkill -9 -f "python -m lingu.core.run"
    ```




- override input_device_index in audio_recorder_client.py with name based "Arctis" search 
- override output_device_index in 





- install vllm
    conda create -n vllm_env python=3.10 -y
    conda activate vllm_env
    pip install vllm
        or:     pip install https://vllm-wheels.s3.us-west-2.amazonaws.com/nightly/vllm-1.0.0.dev-cp38-abi3-manylinux1_x86_64.whl




    pip install vllm
    reinstall torch
    pip uninstall torch torchaudio torchvision    
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

- serve vllm
    conda activate vllm_env
    vllm serve Qwen/Qwen2.5-1.5B-Instruct
    or      vllm serve --gpu-memory-utilization 0.7 Qwen/Qwen2.5-1.5B-Instruct


    vllm serve ./tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --tokenizer TinyLlama/TinyLlama-1.1B-Chat-v1.0


    vllm serve MaziyarPanahi/Qwen2.5-7B-Instruct-abliterated-v2-GGUF/Qwen2.5-7B-Instruct-abliterated-v2.Q5_K_M.gguf


    vllm serve ./Meta-Llama-3.1-8B-Instruct-Q4_K_M-take2.gguf --tokenizer ./Meta-Llama-3.1-8B-Instruct-Q4_K_M-take2.gguf
    vllm serve Qwen/Qwen2.5-1.5B-Instruct
    vllm serve /media/lon/Seagate Backup Plus Drive/Windows/llm/Meta-Llama-3.1-8B-Instruct-Q4_K_M-take2.gguf

    vllm serve ./qwen2.5-32b-agi-q4_k_m.gguf --tokenizer "Qwen/Qwen2.5-7B-Instruct"

 --tokenizer "Qwen/Qwen2.5-7B-Instruct" `
Kills stt server:
sudo pkill -f stt-server


Kills lingus:
sudo pkill -9 -f "python -m lingu.core.run"

Kill all python:
sudo pkill -9 python




DID NOT WORK:
    11:24.7|  [brain] brain initialized
    qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed to load the Qt xcb platform plugin.
    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
    This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

    Available platform plugins are: linuxfb, wayland, offscreen, vnc, minimalegl, vkkhrdisplay, eglfs, xcb, minimal, wayland-egl.

    Aborted (core dumped)
    Command 'python -m lingu.core.run' failed with exit status code '134'.


    TRYING:
    - sudo apt-get install libxcb-cursor0 libx11-xcb1 libxcb1 libxcb-util1 libxrender1 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-shm0 libxcb-sync1 libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1

    SOLVED


DID NOT WORK:
    Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/ui/notify.py", line 298, in check_and_proceed
        callback()    # Call the callback function
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/run.py", line 32, in on_notification_visible
        lingu = Lingu(app)
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/lingu.py", line 34, in __init__
        keyboard.on_press_key("esc", self.on_press)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/__init__.py", line 510, in on_press_key
        return hook_key(key, lambda e: e.event_type == KEY_UP or callback(e), suppress=suppress)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/__init__.py", line 491, in hook_key
        _listener.start_if_necessary()
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/_generic.py", line 35, in start_if_necessary
        self.init()
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/__init__.py", line 196, in init
        _os_keyboard.init()
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/_nixkeyboard.py", line 113, in init
        build_device()
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/_nixkeyboard.py", line 109, in build_device
        ensure_root()
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/keyboard/_nixcommon.py", line 174, in ensure_root
        raise ImportError('You must be root to use this library on linux.')
    ImportError: You must be root to use this library on linux.

    TRYING:
        ```bash
        sudo bash -c "source /home/lon/Dev/Linguflex/Linguflex/installer_files/conda/etc/profile.d/conda.sh && conda activate /home/lon/Dev/Linguflex/Linguflex/installer_files/env && python -m lingu.core.run"
        ```
        
    SOLVED


DID NOT WORK:
    0:03.9|  + importing file lingu.modules.speech.logic
    Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/ui/notify.py", line 298, in check_and_proceed
        callback()    # Call the callback function
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/run.py", line 33, in on_notification_visible
        lingu.start()
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/lingu.py", line 60, in start
        self.modules.load_start_modules()
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 199, in load_start_modules
        self._load(load_start)
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 193, in _load
        self.import_file(module_file, module["folder"], module)
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 87, in import_file
        mod = importlib.import_module(py_file_path)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/importlib/__init__.py", line 126, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
    File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
    File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
    File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
    File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
    File "<frozen importlib._bootstrap_external>", line 883, in exec_module
    File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/modules/speech/logic.py", line 24, in <module>
        from .handlers.engines import Engines
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/modules/speech/handlers/engines.py", line 2, in <module>
        from RealtimeTTS import (
    ImportError: cannot import name 'ParlerEngine' from 'RealtimeTTS' (/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/__init__.py)

    TRYING:
        ```bash
        pip install -U RealtimeTTS[all]
        pip install -U RealtimeSTT
        ```
        
    SOLVED


DID NOT WORK:
Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/lazy_loader/__init__.py", line 230, in load
        parent = inspect.stack()[1]
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/inspect.py", line 1681, in stack
        return getouterframes(sys._getframe(1), context)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/inspect.py", line 1658, in getouterframes
        frameinfo = (frame,) + getframeinfo(frame, context)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/inspect.py", line 1632, in getframeinfo
        lines, lnum = findsource(frame)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/inspect.py", line 952, in findsource
        module = getmodule(object, file)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/inspect.py", line 869, in getmodule
        if ismodule(module) and hasattr(module, '__file__'):
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/importlib/util.py", line 247, in __getattribute__
        self.__spec__.loader.exec_module(self)
    File "<frozen importlib._bootstrap_external>", line 883, in exec_module
    File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/pyautogui/__init__.py", line 246, in <module>
        import mouseinfo
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/mouseinfo/__init__.py", line 223, in <module>
        _display = Display(os.environ['DISPLAY'])
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/Xlib/display.py", line 80, in __init__
        self.display = _BaseDisplay(display)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/Xlib/display.py", line 62, in __init__
        display.Display.__init__(*(self, ) + args, **keys)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/Xlib/protocol/display.py", line 129, in __init__
        raise error.DisplayConnectionError(self.display_name, r.reason)
    Xlib.error.DisplayConnectionError: Can't connect to display ":1": b'Authorization required, but no authorization protocol specified\n'

    During handling of the above exception, another exception occurred:

    Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/ui/notify.py", line 298, in check_and_proceed
        callback()    # Call the callback function
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/run.py", line 33, in on_notification_visible
        lingu.start()
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/lingu.py", line 60, in start
        self.modules.load_start_modules()
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 199, in load_start_modules
        self._load(load_start)
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 193, in _load
        self.import_file(module_file, module["folder"], module)
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/core/modules.py", line 87, in import_file
        mod = importlib.import_module(py_file_path)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/importlib/__init__.py", line 126, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
    File "<frozen importlib._bootstrap>", line 1050, in _gcd_import
    File "<frozen importlib._bootstrap>", line 1027, in _find_and_load
    File "<frozen importlib._bootstrap>", line 1006, in _find_and_load_unlocked
    File "<frozen importlib._bootstrap>", line 688, in _load_unlocked
    File "<frozen importlib._bootstrap_external>", line 883, in exec_module
    File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/modules/speech/logic.py", line 24, in <module>
        from .handlers.engines import Engines
    File "/home/lon/Dev/Linguflex/Linguflex/lingu/modules/speech/handlers/engines.py", line 2, in <module>
        from RealtimeTTS import (
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/__init__.py", line 1, in <module>
        from .text_to_stream import TextToAudioStream  # noqa: F401
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/text_to_stream.py", line 4, in <module>
        from .engines import BaseEngine
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/engines/__init__.py", line 24, in <module>
        from TTS.utils.manage import ModelManager
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/__init__.py", line 16, in <module>
        from TTS.tts.configs.xtts_config import XttsConfig
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/tts/configs/xtts_config.py", line 5, in <module>
        from TTS.tts.models.xtts import XttsArgs, XttsAudioConfig
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/tts/models/xtts.py", line 13, in <module>
        from TTS.tts.layers.xtts.gpt import GPT
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/tts/layers/__init__.py", line 1, in <module>
        from TTS.tts.layers.losses import *
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/tts/layers/losses.py", line 12, in <module>
        from TTS.utils.audio.torch_transforms import TorchSTFT
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/utils/audio/__init__.py", line 1, in <module>
        from TTS.utils.audio.processor import AudioProcessor
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/utils/audio/processor.py", line 11, in <module>
        from TTS.utils.audio.numpy_transforms import (
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/TTS/utils/audio/numpy_transforms.py", line 9, in <module>
        from librosa import magphase, pyin
    File "<frozen importlib._bootstrap>", line 1075, in _handle_fromlist
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/lazy_loader/__init__.py", line 83, in __getattr__
        attr = getattr(submod, name)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/lazy_loader/__init__.py", line 82, in __getattr__
        submod = importlib.import_module(submod_path)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/importlib/__init__.py", line 126, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/librosa/core/spectrum.py", line 17, in <module>
        from .audio import resample
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/librosa/core/audio.py", line 32, in <module>
        samplerate = lazy.load("samplerate")
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/lazy_loader/__init__.py", line 243, in load
        del parent
    UnboundLocalError: local variable 'parent' referenced before assignment

    TRYING:
        xhost +
        - https://stackoverflow.com/questions/31902846/how-to-fix-error-xlib-error-displayconnectionerror-cant-connect-to-display-0
        - https://ubuntuforums.org/showthread.php?t=2290602

    SOLVED


DID NOT WORK:
    stt-server

    (/home/lon/Dev/Linguflex/Linguflex/installer_files/env) lon@lon-MS-7E06:~/Dev/Linguflex/Linguflex$ stt-server
    Could not import the PyAudio C module 'pyaudio._portaudio'.
    Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/bin/stt-server", line 5, in <module>
        from RealtimeSTT_server.stt_server import main
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeSTT_server/stt_server.py", line 67, in <module>
        import pyaudio
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/pyaudio/__init__.py", line 111, in <module>
        import pyaudio._portaudio as pa
    ImportError: /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6: version `GLIBCXX_3.4.32' not found (required by /lib/x86_64-linux-gnu/libjack.so.0)

    TRYING:
        sudo apt update
        sudo apt install libstdc++6
        sudo apt remove libportaudio2 portaudio19-dev
        sudo apt install build-essential autoconf automake libtool
        wget http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
        tar xf pa_stable_v190700_20210406.tgz
        cd portaudio
        ./configure
        make
        sudo make install
        sudo ldconfig
    
    DID NOT WORK

    TRYING:
        mv /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6 \
   /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/libstdc++.so.6.bak

        sudo ldconfig

    SOLVED


DID NOT WORK:

    no stt input

    - changed recording stt to fixed 48000
    - changed recording stt to fixed input device index 0 (it was 9 detected, which was wrong)

    no tts output

    - changed output device index to fixed 9 (default did not work)




























DID NOT WORK:

    specific_model: v2.0.2
    local_models_path: models/xtts
    LOADING CONFIG JSON FROM models/xtts/v2.0.2/config.json
    /home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/trainer/io.py:83: FutureWarning: You are using `torch.load` with `weights_only=False` (the current default value), which uses the default pickle module implicitly. It is possible to construct malicious pickle data which will execute arbitrary code during unpickling (See https://github.com/pytorch/pytorch/blob/main/SECURITY.md#untrusted-models for more details). In a future release, the default value for `weights_only` will be flipped to `True`. This limits the functions that could be executed during unpickling. Arbitrary objects will no longer be allowed to be loaded via this mode unless they are explicitly allowlisted by the user via `torch.serialization.add_safe_globals`. We recommend you start setting `weights_only=True` for any use case where you don't have full control of the loaded file. Please open an issue on GitHub for any issues related to this experimental feature.
    return torch.load(f, map_location=map_location, **kwargs)

    ERROR:root:Error initializing main coqui engine model: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method
    Traceback (most recent call last):
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/engines/coqui_engine.py", line 608, in _synthesize_worker
        tts = load_model(checkpoint, tts)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/RealtimeTTS/engines/coqui_engine.py", line 568, in load_model
        tts.to(torch_device)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 1340, in to
        return self._apply(convert)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 900, in _apply
        module._apply(fn)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 900, in _apply
        module._apply(fn)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 900, in _apply
        module._apply(fn)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 927, in _apply
        param_applied = fn(param)
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/nn/modules/module.py", line 1326, in convert
        return t.to(
    File "/home/lon/Dev/Linguflex/Linguflex/installer_files/env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 305, in _lazy_init
        raise RuntimeError(
    RuntimeError: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method
    Error loading model for checkpoint models/xtts/v2.0.2: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method

