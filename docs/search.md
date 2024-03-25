# Search Module for Linguflex

The Search module for Linguflex enables both text and image search functionalities using the Google Search API.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

The Search module offers two main features:

- **Text Search:** Retrieves real-time information from the internet based on specific search terms.
- **Image Search:** Searches for images on the web and displays them. This feature is particularly useful for obtaining visual content related to the search terms.

## Examples

Text Search:
- "Search the internet for the latest space exploration missions."

Image Search:
- "Show me a picture of the Eiffel Tower at night."

## Installation

### Prerequisites

Before installing the module, you need two key pieces of information from Google:

1. **Google API Key:** For using the Google Search API.
2. **Google Custom Search Engine ID (CSE ID):** To specify the search engine used for the searches.

### Environment Variables

The following environment variables must be set:

- `GOOGLE_API_KEY`
- `GOOGLE_CSE_ID`

These are essential for the module to access and use the Google Search API and the Custom Search Engine.

### Steps to Obtain Google API Key

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Search for "Custom Search API" and enable it.
4. Click "Create Credentials", choose "User data", and proceed.
5. Provide application details and select "Web Application" as the application type.
6. In the "Credentials" section, create an "API Key".
7. Store this key in the `GOOGLE_API_KEY` environment variable or in the `settings.yaml` file.

### Steps to Obtain Google Custom Search Engine ID

1. Visit [Google's Custom Search Engine Site](https://cse.google.com/cse/all).
2. Click "Create a search engine".
3. Name the engine and select "Search the entire web".
4. After creation, locate the "Search engine ID".
5. Store this ID in the `GOOGLE_CSE_ID` environment variable or in the `settings.yaml` file.

## Configuration

### Settings.yaml

As an alternative to setting the environment keys you can also provide the Google API Key and Google Custom Search Engine ID in the `settings.yaml` file. 

**Section:** general (at the top)
- `google_api_key`: Your Google API Key.
- `google_cse_id`: Your Google Custom Search Engine ID.
