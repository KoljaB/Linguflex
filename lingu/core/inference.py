from openai import OpenAI
from .log import log
from .exc import exc
from .events import events
import instructor

MAX_RETRY = 3


class InferenceManager:
    """
    Manages the inference process for various objects using
    either OpenAI's API or a local llm model.

    This class is responsible for setting up and managing the inference
    process for different objects. It lets the LLM fill out a pydantic
    data structure based on the provided prompt and content.
    """
    def __init__(self):
        """
        Initialize the InferenceManager with an OpenAI client.
        """
        self.client = OpenAI()
        self.instructor = None
        self.inference_allowed = True

        events.add_listener(
            "recording_start",
            "listen",
            lambda: self.set_inference_allowed(False))
        events.add_listener(
            "audio_stream_stop",
            "speech",
            lambda: self.set_inference_allowed(True))

    def set_inference_allowed(self, allowed):
        """
        Set whether inference is allowed.

        Args:
            allowed (bool): Whether inference is allowed.
        """
        self.inference_allowed = allowed

    def set_inference_objects(self, inference_objects):
        """
        Set the inference objects to be managed.

        Args:
            inference_objects (list): A list of inference objects.
        """
        self.inf_objs = inference_objects

    def set_instructor(self, instructor):
        """
        Set the instructor to be used for the inference process.

        Args:
            instructor (Instructor): The instructor to be used.
        """
        self.instructor = instructor

    def inference(
            self,
            inference_object,
            prompt,
            content,
            model="gpt-3.5-turbo-1106"):

        if model == "local":
            return self._inference_local(
                inference_object,
                prompt,
                content)
        else:
            return self._inference_openai(
                inference_object,
                prompt,
                content,
                model)

    def _inference_local(
            self,
            inference_object,
            prompt,
            content):
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
        if not self.inference_allowed:
            return None

        for inf_obj in self.inf_objs:
            if inf_obj.name == inference_object and inf_obj.is_internal:

                content_string = f"Content:\n```{content}```"
                messages = [{"role": "user", "content": prompt}]
                messages.append({"role": "user", "content": content_string})

                try:
                    inf_obj.module["state"] = "executing"

                    log.dbg("  [inference] calling local with messages "
                            f"{messages}")
                    events.trigger("inference_start", "inference")
                    extraction_stream = self.instructor(
                        response_model=instructor.Partial[inf_obj.instance],
                        max_retries=MAX_RETRY,
                        messages=messages,
                        max_tokens=500,
                        stream=True,
                    )
                    log.dbg("  [inference] perform extraction")
                    inf_obj.module["state"] = "normal"

                    # obj = None
                    final_extraction = None

                    print("  [inference] extracting ", end="", flush=True)
                    inference_started = False
                    for extraction in extraction_stream:
                        if not inference_started:
                            events.trigger("inference_processing", "inference")
                        inference_started = True
                        if not self.inference_allowed:
                            log.inf("  [inference] local inference stopped "
                                    "(maybe due to recording start event).")
                            final_extraction = None
                            break
                        final_extraction = extraction
                        # obj = extraction.model_dump()
                        # log.dbg(f"  [inference] streaming result: {obj}")
                        print(".", end="", flush=True)

                    events.trigger("inference_end", "inference")
                    print("\n  [inference] extraction done")
                    return final_extraction
                except Exception as e:
                    log.err("  [inference] error performing local inference "
                            f"{inf_obj.instance}: {e}")
                    exc(e)
                    raise e

                # try:
                #     extraction_stream = self.instructor(
                #         response_model=inf_obj.instance,
                #         max_retries=MAX_RETRY,
                #         messages=messages,
                #         max_tokens=500,
                #     )
                #     return extraction_stream
                # except Exception as e:
                #     log.err("  [inference] error using tool "
                #             f"{inf_obj.instance}: {e}")
                #     exc(e)
                #     raise e

        raise Exception(f"Could not find inference object {inference_object}")

    def _inference_openai(
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
            model (str): The model to use for the inference.

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
