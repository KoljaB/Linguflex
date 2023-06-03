# Linguflex

## Worum geht's?
Linguflex ermöglicht die Interaktion mit Textgeneratoren in natürlicher Sprache. 
Es bietet Module zur Verwaltung von Terminkalender und Emails, Abrufen aktueller Infos aus dem Internet ("googlen"), Abspielen von Audio- und Videoinhalten, Smart-Home (Lichtsteuerung), Nachrichten, Wetter und einiges mehr.

## Voraussetzungen
Benötigt wird ein OpenAI API key.  
Dazu Account bei OpenAI eröffnen: https://platform.openai.com/, dann oben rechts auf "Profilnamen / Symbol", im Menü auf "View API Keys" und anschließend auf "Create new secret key".

## Installation
`pip install linguflex`

## Start von Linguflex
`python linguflex`

## Konfiguration
Textdatei mit den zu ladenden Modulen und deren Konfigurationseinstellungen. Es wird empfohlen, mit der einfachen Vanilla-Konfiguration zu beginnen und dann schrittweise Module zu ergänzen. Linguflex lädt die in der config.txt hinterlegte Konfiguration, es sei denn es wird per Kommandozeilenparameter eine andere übergeben.

## Module
In der Sektion [modules] der config-Datei werden die zu ladenden Module angegeben. Linguflex lädt und startet alle Module in der hier angegebenen Reihenfolge.

### Vanilla-Konfiguration

Diese einfache Grundkonfiguration steht initial in der config.txt, ermöglicht Sprachkommunikation und besteht lediglich aus vier Modulen:
- microphone_recorder
- whisper_speechtotext
- openai_generator
- system_texttospeech

Zum starten wird der OpenAI API key in die config.txt in der Sektion [openai_generator] eingetragen.  
```
[openai_generator]
openai_api_key=ENTER YOUR OPENAI API-KEY HERE
```
Konfigurationsparameter der Vanillakonfiguration:
Der Mikrofon-Rekorder nimmt auf, sobald der Eingangspegel über dem in der volume_start_recording festgelegten Schwellwert steigt und beendet die Aufnahme, wenn der Pegel unter den von volume_stop_recording festgelegten Wert fällt.  
Wenn GPT 4 statt GTP 3.5 Turbo verwendet werden soll, den Wert des Parameters gpt_model auf "gpt-4" ändern.
