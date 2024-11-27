from openai import OpenAI, OpenAIError
from .llminterfacebase import LLMInterfaceBase
from lingu import cfg, log
import subprocess
import instructor
import platform
import ollama
import json
import sys


def check_ollama_installed():
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    try:
        subprocess.run(
            ["ollama", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except FileNotFoundError:
        print(f"\n{RED}{BOLD}Ollama CLI not found. It seems Ollama is not installed on your system.{RESET}")
        print(
            f"\n{CYAN}You can configure a different LLM provider like OpenAI, lmstudio, vllm, or OpenRouter "
            f"by updating {BOLD}lingu/settings.yaml{RESET}."
        )
        print(
            f"\n{YELLOW}Choosing 'n' will exit the program.{RESET}"
        )
        print(
            f"\n{YELLOW}Would you like me to try install Ollama now? (y/n){RESET}"
        )

        choice = input().strip().lower()
        if choice == 'y':
            print(f"{CYAN}Attempting to install Ollama...{RESET}")
            try:
                if platform.system() == "Windows":
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "ollama"],
                        check=True
                    )
                elif platform.system() == "Linux":
                    subprocess.run(
                        "curl -fsSL https://ollama.com/install.sh | sh",
                        shell=True,
                        check=True
                    )
                else:
                    print(f"{RED}{BOLD}Unsupported operating system for automatic installation.{RESET}")
                    sys.exit(1)
                # Retry after installation
                subprocess.run(
                    ["ollama", "--version"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                print(f"{GREEN}{BOLD}Ollama installed successfully!{RESET}")
            except Exception as e:
                os_hint = "Windows" if platform.system() == "Windows" else "Linux"
                print(f"{RED}{BOLD}Failed to install Ollama: {e}{RESET}")
                print(
                    f"\n{YELLOW}Please visit {CYAN}https://ollama.com/download{RESET}{YELLOW}, select the "
                    f"correct download for your operating system ({BOLD}{os_hint}{RESET}{YELLOW}), "
                    f"and follow the instructions. After installation, restart this program.{RESET}"
                )
                sys.exit(1)
        else:
            print(f"{RED}{BOLD}Ollama installation skipped. Exiting...{RESET}")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print(f"{RED}{BOLD}An error occurred while checking Ollama version.{RESET}")
        sys.exit(1)

class OllamaInterface(LLMInterfaceBase):
    def __init__(self, history, model_path=None, model_name=None, vision_model_name=None):
        check_ollama_installed()

        model_name = model_name or cfg("local_llm", "model_name", default="llama3.1:8b")

        function_calling_model_name = cfg(
            "local_llm", "function_calling_model_name",
            default=model_name)

        vision_model_name = vision_model_name or cfg("see", "model_name", default="llava")
        self.vision_model = vision_model_name
        ollama_url = cfg("local_llm", "ollama_url", default="http://127.0.0.1:11434/v1")


        llama = OpenAI(base_url=ollama_url, api_key="dummy")
        create = instructor.patch(
            create=llama.chat.completions.create,
            mode=instructor.Mode.JSON_SCHEMA
        )
        super().__init__(history, model_name, function_calling_model_name, llama, create)

    def warm_up_safe(self):
        self.warm_up_with_error_handling()

    def warm_up(self):
        """
        A simple warmup function that sends a basic prompt to the model
        to ensure it's working correctly. If there's an error, it raises
        an OpenAIError.
        """
        try:
            log.inf("  [brain] warming up the Ollama model...")
            response = self.llama.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": "Hello, how can I assist you today?"}]
            )
            if response and len(response.choices) > 0:
                log.inf("  [brain] ollama model is ready and responsive")
            else:
                raise OpenAIError("Warmup failed: Model did not respond as expected.")
        except OpenAIError as e:
            raise OpenAIError(f"Warmup failed: {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during warmup: {str(e)}")        

    def warm_up_with_error_handling(self, last_try = False):
        log.dbg("  performing warmup with error handling")
        try:
            self.warm_up()
        except OpenAIError as e:
            # Check if the error is specifically about the model not being found
            if "model" in str(e):
                log.inf(f"  [brain] model {self.model_name} not found. Attempting to pull the model...")
                self.pull_model(self.model_name)
                self.warm_up()
            else:
                log.err(f"  [brain] Unexpected OpenAI error: {e}")
                log.err(f"  [brain] Exception type: {type(e).__name__}")  # Log the exception type
                sys.exit(1)

        except Exception as e:  # Catch any other unknown error
            log.err(f"  [brain] An unknown error occurred: {e}")
            log.err(f"  [brain] Exception type: {type(e).__name__}")  # Log the exception type
            sys.exit(1)

    def run_model(self, model_name):
        try:
            subprocess.run(["ollama", "run", model_name], check=True)
            log.inf(f"  [brain] successfully running model: {model_name}")
        except subprocess.CalledProcessError as e:
            log.err(f"  [brain] failed to run model {model_name}. Error: {e}")
            sys.exit(1)

    def pull_model(self, model_name):
        try:
            subprocess.run(["ollama", "pull", model_name], check=True)
            log.inf(f"  [brain] successfully pulled model: {model_name}")
        except subprocess.CalledProcessError as e:
            log.err(f"  [brain] failed to pull model {model_name}. Error: {e}")
            sys.exit(1)

    def generate_image(
            self,
            messages,
            prompt: str,
            image_path: str,
            image_source: str
    ):
        self.abort = False
        self.tool_executed = False

        if image_source == "screen":
            image_source = "desktop screenshot"

        full_prompt = f"This image was captured from a {image_source}.\nCarefully check this image to answer the following user request:\n{prompt}"

        messages = [
            {
                'role': 'user',
                'content': full_prompt,
                'images': [image_path]
            }
        ]

        log.inf(f"  [brain] calling ollama vision model {self.vision_model} with messages:")
        log.inf('=>{}'.format(json.dumps(messages, indent=4)))

        try:
            response = ollama.chat(
                model=self.vision_model,
                messages=messages, 
                stream=True
            )

            log.inf('  <= stream')

            if not self.abort:
                for chunk in response:
                    if self.abort:
                        break
                    content = chunk['message']['content']
                    if content:
                        yield content
        except Exception as e:
            log.err(f"  [brain] Error in generate_image: {str(e)}")
            yield f"An error occurred while processing the image: {str(e)}"
