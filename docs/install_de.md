# Linguflex Installationsanleitung

## Schritt 1: OpenAI API-Schlüssel einrichten
*ermöglicht Zugriff auf die KI-API*

1. Konto auf der [OpenAI Anmeldeseite](https://platform.openai.com/signup) erstellen.
2. Oben rechts auf den Namen klicken und "View API keys" wählen.
3. Auf "Create new secret key" klicken und einen neuen API-Schlüssel generieren.

## Schritt 2: Python installieren
*stellt die Softwareplattform bereit, auf der Linguflex konstruiert wurde*

1. [Python 3.9.9 Installationsseite](https://www.python.org/downloads/release/python-399/) aufrufen
   (Python 3.9.9, da Whisper auf dieser Version trainiert und getestet wurde)
2. Nach unten scrollen und "Windows installer (64-bit)" wählen. Dies gilt für die meisten Systeme.

## Schritt 3: FFmpeg installieren
*liefert die für die Spracherkennung von Whisper benötigte Bibliothek*

1. Laden Sie die [ZIP-Datei der neuesten FFmpeg-Version](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z) von https://www.gyan.dev/ffmpeg/builds/ herunter.
2. Entpacken Sie diese Datei mit einem beliebigen Archivierungsprogramm wie 7zip oder Winrar.
3. Benennen Sie den entpackten Ordner in 'ffmpeg' um und verschieben Sie ihn in den Hauptordner Ihres C: Laufwerks.
4. Öffnen Sie die Eingabeaufforderung mit Administratorrechten und führen Sie den folgenden Befehl aus:
   ```bash
   setx /m PATH "C:\ffmpeg\bin;%PATH%"
5. Starten Sie den Computer neu. Sie können die Installation überprüfen, indem Sie folgenden Befehl ausführen:
   ```bash
   ffmpeg -version
   ```

## Step 4: [Optional] PyTorch mit CUDA-Unterstützung installieren
*ermöglicht schnellere (GPU-basierte) Spracherkennung durch Whisper*

> Hinweis: Dieser Schritt ist optional, doch sehr empfehlenswert, sollte eine Grafikkarte aus [dieser Liste](https://developer.nvidia.com/cuda-gpus) vorliegen 

1. [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive) installieren.
2. Eingabeaufforderung öffnen und folgenden Befehl ausführen:
   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Schritt 5: Linguflex herunterladen

1. [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip) herunterladen.
2. ZIP-Datei in den gewünschten Installationsordner von Linguflex entpacken.

## Schritt 6: Linguflex installieren

1. Eingabeaufforderung öffnen 
2. Zum Installationsordner aus Schritt 5.2 navigieren
3. Folgenden Befehl ausführen:
   ```bash
   pip install -r requirements.txt
   ```
4. (optional, aber empfohlen) tiktoken upgraden
   ```bash
   pip install --upgrade tiktoken
   ```

## Schritt 7: Linguflex starten

Jetzt ist das System bereit, die Grundversion von Linguflex zu starten.

Dazu folgende Batchdatei im Installationsordner von Linguflex ausführen:

```bash
start_linguflex
```

Alternativ: python linguflex.py

## Nach der Installation

### Module einrichten

Nach der Installation der Grundversion kann die Kernfunktionalität durch hinzufügen von Modulen erweitert werden.  

Bitte lesen Sie die folgenden Dokumente, um loszulegen:

[Modulinstallationsanleitung](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md)

[Konfigurationsanleitung](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md)

### Mikrophon kalibrieren

Nach dem erfolgreichen Start von Linguflex, ist es vorteilhaft, das Mikrofon zu kalibrieren:

1. Setzen Sie `debug_show_volume = True` in der Datei `config.txt` unter dem Abschnitt `[microphone_recorder]`.
2. Starten Sie Linguflex und beobachten Sie die Lautstärkepegel in der Ausgabe.
3. Schreiben Sie geeignete Werte für `volume_start_recording` und `volume_stop_recording` in die Datei `config.txt`.

### Inbetriebnahme der restlichen Module

Die Grundversion von Linguflex kann nun gestartet werden.  
Anschließend können Module in der Konfigurationsdatei hinzugefügt werden, um die Funktionalität von Linguflex zu erweitern.

Wählen Sie dazu ein Modul aus der Liste im [modules]-Abschnitt der Konfigurationsdatei aus und kommentieren Sie es aus. Befolgen Sie die Beschreibung in der [Modulinstallationsanleitung](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md) und der [Konfigurationsanleitung](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md), um das Modul einzurichten.
