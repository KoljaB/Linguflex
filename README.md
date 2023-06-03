# Linguflex

## Worum geht's?

Linguflex ermöglicht die Interaktion mit Textgeneratoren in natürlicher Sprache. 
Es bietet Module zur Verwaltung von Terminkalender und Emails, Smart-Home-Aufgaben wie zB Lichtsteuerung, Nachrichten, Wetter, Abrufen aktueller Infos aus dem Internet ("googlen"), Abspielen von Audio- und Videoinhalten und einiges mehr.

## Voraussetzungen

Benötigt wird ein OpenAI API key. Dazu Account bei OpenAI eröffnen: https://platform.openai.com/. Oben rechts auf "Profilnamen / Symbol", im Menü auf "View API Keys" und anschließend "Create new secret key".

## Installation

`pip install linguflex`

## Start von Linguflex

`python linguflex`

## Konfiguration

Es wird empfohlen, mit der Vanilla-Konfiguration zu beginnen und dann schrittweise Module zu ergänzen. Linguflex lädt immer die in der config.txt hinterlegte Konfiguration, es sei denn es wird per Kommandozeilenparameter eine andere übergeben.

### Vanilla-Konfiguration
Diese einfache Grundkonfiguration steht initial in der config.txt, ermöglicht Sprachkommunikation und besteht lediglich aus vier Modulen:
- microphone_recorder
- whisper_speechtotext
- openai_generator
- system_texttospeech

Zum starten wird der OpenAI API key in die config.txt eingetragen.
`[openai_generator]
openai_api_key=ENTER YOUR OPENAI API-KEY HERE`
