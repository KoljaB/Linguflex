# Brain Module for Linguflex

The Brain module for Linguflex handles natural language processing with both local and OpenAI's language models.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

This module supports

- Generating textual responses based on user input.
- Integration of both local language models and OpenAI's GPT models.
- Handling of history and state of conversations.

## Examples

- "Tell me a joke about computers."

## Installation

### Environment Variables

`OPENAI_API_KEY`

To use openai with this module an OpenAI API Key must be set as the environment variable `OPENAI_API_KEY`.

To obtain an API key:

1. Create an account on the [OpenAI signup page](https://platform.openai.com/signup).
2. Click on the name at the top right and select "View API keys".
3. Click on "Create new secret key" and generate a new API key.

## Configuration

### Settings.yaml

Configure the Brain module by editing the `settings.yaml` file

**Section:** general (at the top)
- `openai_model` - Set to specify the OpenAI model to use.
- `max_history_messages` Maximum number of history messages to keep.

**Section:** local_llm
- `gpu_layers`: Number of GPU layers to use.
- `model_path`: Path to the local language model directory.
- `model_name`: Filename of the local language model.
- `max_retries`: Maximum retries for LLM requests.
- `context_length`: Context length for language model.
- `max_tokens`: Maximum tokens in a single response.
- `repeat_penalty`: Penalty for repeated content.
- `temperature`: Controls randomness.
- `top_p`: Top probability for token selection.
- `top_k`: Top K tokens to consider for generation.
- `tfs_z`: Transformer factorization setting.
- `mirostat_mode`: Mirostat mode.
- `mirostat_tau`: Mirostat time constant.
- `mirostat_eta`: Mirostat learning rate.
- `verbose`: Verbose logging.
- `threads`: Number of threads for processing.
- `rope_freq_base`: Rope frequency base.
- `rope_freq_scale`: Rope frequency scale.

**Section:** see
- `vision_model`: Specify the vision model for image-related tasks.
- `vision_max_tokens`: Maximum tokens for vision tasks.

