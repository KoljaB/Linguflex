# Linguflex Installationsanleitung

Bitte folgen Sie diesen Schritten, um eine erfolgreiche Installation von Linguflex zu gewährleisten.

## Schritt 1: OpenAI API-Schlüssel erstellen

1. Erstellen Sie einen Account auf der [OpenAI Anmeldeseite](https://platform.openai.com/signup).
2. Nach dem Einloggen klicken Sie oben rechts auf Ihren Namen und wählen "View API keys".
3. Klicken Sie auf "Create new secret key" und generieren Sie einen neuen API-Schlüssel.

## Schritt 2: Python installieren

1. Besuchen Sie die [Python 3.9.9 Installationsseite](https://www.python.org/downloads/release/python-399/).
2. Scrollen Sie nach unten und wählen Sie "Windows installer (64-bit)". Dies gilt für die meisten Systeme.

## Schritt 3: Linguflex herunterladen

1. Laden Sie [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip) herunter.
2. Entpacken Sie die ZIP-Datei an Ihrem gewünschten Ort.

## Schritt 4: [Optional] PyTorch mit CUDA-Unterstützung installieren

> Hinweis: Dieser Schritt ist optional, ermöglicht jedoch eine schnellere Spracherkennung durch die Nutzung Ihrer Grafikkarte. Funktioniert nur mit [bestimmten Nvidia-Grafikkarten](https://developer.nvidia.com/cuda-gpus).

1. Installieren Sie [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive).
2. Öffnen Sie die Eingabeaufforderung und führen Sie den folgenden Befehl aus:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Schritt 5: Linguflex installieren

1. Öffnen Sie die Eingabeaufforderung.
2. Navigieren Sie zu dem Ordner, den Sie in Schritt 3 erstellt haben.
3. Führen Sie den folgenden Befehl aus:
   ```bash
   pip install -r requirements.txt
   ```

## Schritt 6: Linguflex starten

Führen Sie den folgenden Befehl in Ihrer Eingabeaufforderung aus:

```bash
python linguflex
```

## Nach der Installation: Mikrofonkalibrierung

Nach dem erfolgreichen Start von Linguflex wäre es hilfreich, Ihr Mikrofon zu kalibrieren:

1. Setzen Sie `debug_show_volume = True` in der `config.txt` Datei unter der Sektion `[microphone_recorder]`.
2. Starten Sie Linguflex und beobachten Sie die Lautstärkepegel in der Ausgabe.
3. Schreiben Sie geeignete Werte für `volume_start_recording` und `volume_stop_recording` in die `config.txt` Datei.
