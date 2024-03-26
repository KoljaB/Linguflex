# Calendar Module for Linguflex

The Calendar module for Linguflex enables users to manage their Google Calendar events. It allows for the retrieval, addition, modification, and deletion of calendar events.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

This module offers several functionalities for interacting with Google Calendar:

- **Retrieve Calendar Events**: Allows users to get current events from their Google Calendar.
- **Add Calendar Event**: Enables users to add new events to their calendar. 
- **Move Calendar Event**: Permits users to reschedule existing events to a new time or date.
- **Delete Calendar Event**: Provides the ability to remove events from the calendar.

## Examples

- "Show me my events for today."
- "Add a meeting event on March 30th at 2 PM."
- "Move my appointment from April 5th to April 6th."
- "Delete the team lunch event on May 1st."

## Installation

### Google Calendar API Credentials

Before using the Calendar module, you must obtain a `credentials.json` file from Google. This file is necessary for authenticating with the Google Calendar API. Follow these steps to obtain it:

1. Visit the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project or select an existing project.
3. Enable the Google Calendar API by clicking on "Enable APIs and Services", searching for "Google Calendar API", and then clicking "Enable".
4. Generate credentials by clicking "Credentials" in the sidebar, selecting "Create credentials", and choosing "OAuth client ID".
5. Set up the OAuth consent screen by providing the required information.
6. Select "Desktop app" as the application type and click "Create".
7. Download the `credentials.json` file after creating your credentials.

Place the `credentials.json` file in the executing directory of Linguflex.

## Configuration

### Settings.yaml

**Section:** calendar

- `timezone`: Your preferred timezone. Default is set to "Europe/Berlin". Make sure to update this to reflect your local timezone.
- `credentials_file_path`: The path to your `credentials.json` file. The default path is set to "credentials.json" in the executing directory.

It is crucial to ensure that your `credentials.json` file is in the correct location and that your `timezone` is set accurately to ensure proper functionality of the Calendar module.