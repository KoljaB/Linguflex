from openai import OpenAI
from .log import log
from .exc import exc

MAX_RETRY = 3


class InferenceManager:
    """
    Manages the inference process for various objects using OpenAI's API.

    This class is responsible for setting up and managing the inference
    process for different objects. It interacts with OpenAI's API to
    perform tasks based on the provided inference objects.

    Attributes:
        client (OpenAI): The client instance for interacting with OpenAI's API.
        inf_objs (list): List of inference objects to be managed.
    """
    def __init__(self):
        """
        Initialize the InferenceManager with an OpenAI client.
        """
        self.client = OpenAI()

    def set_inference_objects(self, inference_objects):
        """
        Set the inference objects to be managed.

        Args:
            inference_objects (list): A list of inference objects.
        """
        self.inf_objs = inference_objects

    def inference(
            self,
            inference_object,
            prompt,
            content,
            model="gpt-3.5-turbo-1106"):
        """
        Perform inference using the specified object, prompt, and content.

        Args:
            inference_object (str): The name of the inference object to use.
            prompt (str): The prompt to be used for the inference.
            content (str): The content to be analyzed or processed.

        Raises:
            Exception: If the inference object is not found or if the maximum
                       number of retries is reached without success.

        Returns:
            Any: The result of the inference process.
        """
        for inf_obj in self.inf_objs:
            if inf_obj.name == inference_object and inf_obj.is_internal:

                content_string = f"Content:\n```{content}```"
                messages = [{"role": "user", "content": prompt}]
                messages.append({"role": "user", "content": content_string})
                tools = []
                fct_dict = {
                    "type": "function",
                    "function": inf_obj.schema
                }
                tools.append(fct_dict)
                log.dbg("  [inference] calling openai with messages "
                        f"{messages} and tools {tools}")

                retry = 0
                while retry < MAX_RETRY:
                    tool_id = ""
                    try:
                        response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=0,
                            tools=tools,
                            tool_choice={
                                "type": "function",
                                "function": {
                                    "name": inference_object
                                }
                            }
                        )
                        response_message = response.choices[0].message
                        tool_calls = response_message.tool_calls
                        if tool_calls:
                            for tool_call in tool_calls:
                                obj = inf_obj.info_dict["obj"]
                                tool_id = tool_call.id

                                try:
                                    class_instance = obj.from_function_call(
                                        tool_call.function)
                                except Exception as e:
                                    print(f"function: {tool_call.function}")
                                    log.err("  [inference] error using tool "
                                            f"{inference_object}: {e}")
                                    exc(e)
                                    raise e

                                return class_instance
                    except Exception as e:
                        if tool_id:
                            messages += {
                                "tool_call_id": tool_id,
                                "role": "tool",
                                "name": inference_object,
                                "content": {e}
                            }
                            msg = "Call the tool again considering the error."
                            messages += {
                                "role": "user",
                                "content": msg
                            }
                        else:
                            msg = f"Error calling tool: {e}\n\n"
                            "Call the tool again considering the error."
                            messages += {
                                "role": "user",
                                "content": msg
                            }

                        log.err("  [inference] error using tool "
                                f"{inference_object}: {e}")
                        exc(e)
                        raise e

                    retry += 1

                if retry == MAX_RETRY:
                    raise Exception(
                        "Could not complete inference for "
                        f"{inference_object} after {MAX_RETRY} retries")

        raise Exception(f"Could not find inference object {inference_object}")
