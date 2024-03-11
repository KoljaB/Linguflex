# Mail Module for Linguflex

The Mail module for Linguflex retrieves emails, summarizes their content, assesses their importance, and extracts links.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Configuration](#configuration)

## Functionality

The Mail module performs several key functions:

- Retrieves emails from a specified server.
- Summarizes the content of the emails.
- Assesses the importance of each email on a scale from 0 to 10.
- Extracts the first 3 links from each email.

## Examples

- "Give me a summary of emails from the last 12 hours."
- "Summarize the latest email from my manager."
- "Check if there are any important emails about the project update."
- "Tell me the links from the newsletter I received this morning."

## Configuration

### Settings.yaml

**Section:** mail

- `server`: Server from which to retrieve emails (e.g., imap.web.de).
- `username`: Username for the email account.
- `password`: Password for the email account.
- `history_hours`: Number of hours to look into the past for mail retrieval.
- `max_mail_length`: The number of characters to which the email will be truncated. This is due to the limited context window of large language models (LLMs) for summarizing.
- `summary_prompt`: The prompt used by the LLM to summarize the email.
- `importance_threshold`: The minimum importance score (0-10) an email must have to be considered important when filtering.
- `summarize_model`: 
  - Set to "local" to use the LLM defined in the local_llm section for summarization, link extraction, and importance classification.
  - Set to an OpenAI model name (e.g., "gpt-3.5-turbo-1106" or "gpt-4-0125-preview") to use an OpenAI model for these tasks.

