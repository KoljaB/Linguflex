# Linguflex Installationsanleitung

Folgend Schritte sollten eine erfolgreiche Installation gewährleisten:

## Schritt 1: OpenAI API-Schlüssel erstellen

1. Account auf der [OpenAI Anmeldeseite](https://platform.openai.com/signup) erstellen.
2. Nach dem Einloggen oben rechts auf den Namen klicken und "View API keys" wählen.
3. Auf "Create new secret key" klicken und einen neuen API-Schlüssel generieren.

## Schritt 2: Python installieren

1. [Python 3.9.9 Installationsseite](https://www.python.org/downloads/release/python-399/) aufrufen
2. Nach unten scrollen und "Windows installer (64-bit)" wählen. Dies gilt für die meisten Systeme.

## Schritt 3: Linguflex herunterladen

1. [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip) herunterladen.
2. ZIP-Datei am gewünschten Ort entpacken.

## Schritt 4: [Optional] PyTorch mit CUDA-Unterstützung installieren

> Hinweis: Dieser Schritt ist optional und ermöglicht eine schnellere Spracherkennung durch die Nutzung der Grafikkarte. Wenn eine Grafikkarte aus [dieser Liste](https://developer.nvidia.com/cuda-gpus) vorliegt, empfehle ich diesen Extraschritt.

1. [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive) installieren.
2. Eingabeaufforderung öffnen und folgenden Befehl ausführen:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Schritt 5: Linguflex installieren

1. Eingabeaufforderung öffnen 
2. Zum Ordner aus Schritt 3 navigieren
3. Folgenden Befehl ausführen:
   ```bash
   pip install -r requirements.txt
   ```
4. (optional) tiktoken upgraden
   ```bash
   pip install --upgrade tiktoken
   ```

## Schritt 6: Linguflex starten

Folgende Batchdatei im Ordner aus Schritt 3 ausführen:

```bash
start_linguflex
```

Alternativ: python linguflex.py

## Nach der Installation

### Mikrofonkalibrierung

Nach dem erfolgreichen Start von Linguflex sollte man das Mikrofon kalibrieren:

1. `debug_show_volume = True` setzen in der `config.txt` Datei unter der Sektion `[microphone_recorder]`.
2. Linguflex starten und Lautstärkepegel in der Ausgabe beobachten.
3. Geeignete Werte für `volume_start_recording` und `volume_stop_recording` in die `config.txt` Datei schreiben.

### Inbetriebnahme der restlichen Module

Schnellste Methode:
- Datei start_linguflex.bat im Texteditor öffnen
- API Keys von den dort angegeben Webseiten besorgen und dort eintragen
