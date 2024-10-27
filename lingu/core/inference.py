from openai import OpenAI
from .log import log
from .exc import exc
from .settings import cfg
from .events import events
import instructor
from instructor import patch

MAX_RETRY = 3

function_calling_model_name = cfg(
    "local_llm", "function_calling_model_name",
    default=cfg(
    "local_llm", "model_name",
    default="llama3.1:8b"))

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
        self.instructor = None
        self.llama = None
        self.openai_instructor = None
        self.inference_allowed = True

        events.add_listener(
            "recording_start",
            "listen",
            lambda: self.set_inference_allowed(False))
        events.add_listener(
            "audio_stream_stop",
            "speech",
            lambda: self.set_inference_allowed(True))

    def llm(self, **kwargs):
        """
        Ask LLM things from logic etc

        Args:
            **kwargs: Parameters to call.
        """
        kwargs['model'] = function_calling_model_name
        response = self.llama.chat.completions.create(**kwargs)        
        return response

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

    def set_instructor(self, instructor, llama):
        """
        Set the instructor to be used for the inference process.

        Args:
            instructor (Instructor): The instructor to be used.
            llama: LLama object for direct llm communication
        """
        self.instructor = instructor
        self.llama = llama

    def inference(
            self,
            inference_object,
            prompt,
            content,
            model="gpt-3.5-turbo-1106"):
        
        print (f"INFERENCE MODEL: {model}")

        if model == "local":
            return self._inference_local(
                inference_object,
                prompt,
                content)
        elif model == "ollama":
            return self._inference_ollama(
                inference_object,
                prompt,
                content)
        else:
            return self._inference_openai(
                inference_object,
                prompt,
                content,
                model)

    def _inference_ollama(self, inference_object, prompt, content):
        """
        Perform inference using the specified object, prompt, and content with Ollama model.

        Args:
            inference_object (str): The name of the inference object to use.
            prompt (str): The prompt to be used for the inference.
            content (str): The content to be analyzed or processed.

        Raises:
            Exception: If the inference object is not found or if the maximum number of retries is reached without success.

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

                    log.dbg("  [inference] calling Ollama with messages " f"{messages}")
                    events.trigger("inference_start", "inference")
                    extraction_stream = self.instructor(
                        model=function_calling_model_name,
                        response_model=instructor.Partial[inf_obj.instance],
                        max_retries=MAX_RETRY,
                        messages=messages,
                        temperature=0,
                        max_tokens=1000,
                        stream=True,
                    )
                    log.dbg("  [inference] perform extraction")
                    inf_obj.module["state"] = "normal"

                    print("  [inference] extracting ", end="", flush=True)
                    inference_started = False
                    final_extraction = None
                    for extraction in extraction_stream:
                        if not inference_started:
                            events.trigger("inference_processing", "inference")
                        inference_started = True
                        if not self.inference_allowed:
                            log.inf("  [inference] Ollama inference stopped " "(maybe due to recording start event).")
                            final_extraction = None
                            break
                        final_extraction = extraction
                        print(".", end="", flush=True)

                    events.trigger("inference_end", "inference")
                    print("\n  [inference] extraction done")
                    return final_extraction
                except Exception as e:
                    log.err("  [inference] error performing Ollama inference " f"{inf_obj.instance}: {e}")
                    exc(e)
                    raise e

        raise Exception(f"Could not find inference object {inference_object}")

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
                        temperature=0,
                        max_tokens=1000,
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
                        print(".", end="", flush=True)

                    events.trigger("inference_end", "inference")
                    print("\n  [inference] extraction done")
                    return final_extraction
                except Exception as e:
                    log.err("  [inference] error performing local inference "
                            f"{inf_obj.instance}: {e}")
                    exc(e)
                    raise e

        raise Exception(f"Could not find inference object {inference_object}")

    def verify_openai_client(self):
        if not self.openai_instructor:
            self.client = OpenAI()
            client = patch(OpenAI())
            self.openai_instructor = client.chat.completions.create

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

        self.verify_openai_client()

        for inf_obj in self.inf_objs:
            if inf_obj.name == inference_object and inf_obj.is_internal:

                content_string = f"Content:\n```{content}```"
                messages = [{"role": "user", "content": prompt}]
                messages.append({"role": "user", "content": content_string})

                try:
                    inf_obj.module["state"] = "executing"

                    log.dbg("  [inference] calling openai with messages "
                            f"{messages}")
                    events.trigger("inference_start", "inference")
                    extraction_stream = self.openai_instructor(
                        model=model,
                        response_model=instructor.Partial[inf_obj.instance],
                        max_retries=MAX_RETRY,
                        messages=messages,
                        temperature=0,
                        max_tokens=1000,
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
