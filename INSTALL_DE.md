# Installation

## 1. OpenAI API Key anlegen

- Account anlegen auf https://platform.openai.com/signup
- einloggen, dann rechts oben auf den Namen und auf "View API keys" klicken
- auf "Create new secret key" klicken und neuen API Key erstellen

## 2. Python installieren

- [Installationsseite für Python 3.9.9](https://www.python.org/downloads/release/python-399/) aufrufen
- ganz unten "Windows installer (64-bit)" auswählen (in den in den meisten Fällen zumindest) 
 
## 3. Linguflex herunterladen

- [Linguflex](https://github.com/KoljaB/Linguflex/archive/refs/heads/main.zip) herunterladen
- das ZIP File in den gewünschten Ordner entpacken
  
## 4. [Optional] PyTorch mit CUDA-Support installieren
- schnellere Spracherkennung durch Nutzung der Grafikkarte (nicht unbedingt benötigt)
- funktioniert nur mit [bestimmten Nvidia-Grafikkarten](https://developer.nvidia.com/cuda-gpus)
- [Nvidia CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive) installieren
- Eingabeaufforderung öffnen und ausführen:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 5. Linguflex installieren
- Eingabeaufforderung öffnen
- zum Ordner wechseln, der unter #3 angelegt wurde
- folgenden Befehl ausführen:
```
pip install -r requirements.txt
```

## 6. Linguflex starten
```
python linguflex
```

---

Damit läuft das Grundsystem.  
Sinnvoll als erster Schritt nach dem Start-Test:

## Mikrophon-Kalibrierung
- debug_show_volume = True setzen in der config.txt unter [microphone_recorder]
- Linguflex starten und Pegelwerte in der Ausgabe beobachten
- geeignete Werte für `volume_start_recording` und `volume_stop_recording` in die config.txt schreiben
