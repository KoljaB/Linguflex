from .events import events
from .prompt import Prompt
from .exc import exc
from .log import log
from .settings import cfg
import re


called_tool_messages = int(cfg("called_tool_messages", default="1"))


class Tools:
    """
    Handles LLM Tool calling
    """

    def __init__(self, inf_objs):
        """
        Initialize the Tools instance.

        Args:
            inf_objs (List): A list of inference objects available
              for execution.
        """
        self.prompt = Prompt("")
        self.inf_objs = inf_objs
        self.executed_tools = []

        events.add_listener(
            "function_call_request",
            "brain",
            self.execute_tool)

    def start_execution(self):
        """
        Initiates the execution process.
        """
        self.prompt.start()

    def get_prompt(self):
        """
        Retrieves the current prompt.
        """
        return self.prompt.get()

    def get_tool_by_name(self, name):
        """
        Retrieves the tool by name.

        Args:
            name (str): The name of the tool to retrieve.

        Returns:
            Dict: The tool information.
        """
        for inf_obj in self.inf_objs:
            if inf_obj.name == name:
                return inf_obj
        return None

    def execute_tool(self, tool):
        """
        Executes the specified tool.

        Args:
            tool (Dict): A dictionary containing tool information.

        Returns:
            str: The result of the tool execution.
        """
        log.inf(f"Tool execution requested: {tool['name']}")

        return_value = "fail, reason: tool not found"
        tool["executed"] = False

        for inf_obj in self.inf_objs:
            log.inf(f"  comparing {inf_obj.name} to tool {tool['name']}")
            if inf_obj.name == tool["name"]:

                log.dbg(f"  found tool {inf_obj.name}")

                if inf_obj.is_invokable:
                    inf_obj.execute_count = called_tool_messages
                    inf_obj.module["state"] = "executing"
                    execute = inf_obj.info_dict["execution"]
                    args = tool["arguments"]
                    try:
                        events.trigger_with_params(
                            event_name="function_call",
                            triggering_module="brain",
                            tool=tool,
                            inf_obj=inf_obj
                        )
                        return_value = execute.from_arguments(args)
                        if "success_prompt" in inf_obj.language_info:
                            self.prompt.add(
                                inf_obj.language_info["success_prompt"]
                            )
                    except Exception as e:
                        return_value = f"fail, reason: {str(e)}"
                        if "fail_prompt" in inf_obj.language_info:
                            self.prompt.add(
                                inf_obj.language_info["fail_prompt"]
                            )
                        exc(e)
                elif inf_obj.is_populatable:
                    inf_obj.execute_count = called_tool_messages
                    inf_obj.module["state"] = "executing"
                    obj = inf_obj.info_dict["obj"]
                    args = tool["arguments"]
                    try:
                        events.trigger_with_params(
                            event_name="function_call",
                            triggering_module="brain",
                            tool=tool,
                            inf_obj=inf_obj
                        )
                        class_instance = obj.from_arguments(args)
                        if hasattr(class_instance, 'on_populated'):
                            log.dbg("  calling on_populated for "
                                    f"{inf_obj.name}")
                            return_value = class_instance.on_populated()
                        else:
                            return_value = "success"

                        print("Checking for success prompt in "
                              f"{inf_obj.language_info}")
                        if "success_prompt" in inf_obj.language_info:
                            print("Adding success prompt "
                                  f"{inf_obj.language_info['success_prompt']}")
                            self.prompt.add(
                                inf_obj.language_info["success_prompt"])
                    except Exception as e:
                        return_value = f"fail, reason: {str(e)}"
                        if "fail_prompt" in inf_obj.language_info:
                            self.prompt.add(
                                inf_obj.language_info["fail_prompt"])
                        exc(e)

                inf_obj.module["state"] = "normal"

                events.trigger_with_params(
                    event_name="function_call_finished",
                    triggering_module="brain",
                    tool=tool,
                    inf_obj=inf_obj
                )

                log.dbg(f"  tool {inf_obj.name} executed, "
                        f"return value: {return_value}")
                tool["executed"] = True
                break

        tool["return_value"] = return_value
        if tool["executed"]:
            self.executed_tools.append(tool)
            
        return return_value

    def get_tools(self, text: str):
        """
        Retrieves the list of tools based on the provided text.

        Args:
            text (str): The text to analyze for tool extraction.

        Returns:
            List[Dict]: A list of tools relevant to the provided text.
        """
        functions = []

        for inf_obj in self.inf_objs:

            if inf_obj.is_internal:
                continue

            # print(f"  checking {inf_obj.name}")
            # print(f"  keywords {inf_obj.language_info.get('keywords', None)}")

            if "keywords" in inf_obj.language_info and \
                    inf_obj.language_info["keywords"] and \
                    len(inf_obj.language_info["keywords"]) > 0:

                keywords_in_input = [
                    keyword for keyword in inf_obj.language_info["keywords"]
                    if re.search(
                        r"\b" + keyword.lower().replace("*", ".*") + r"\b",
                        text.lower()
                    )
                ]

            else:
                if "init_prompt" in inf_obj.language_info:
                    if inf_obj.language_info["init_prompt"]:
                        init_prompt = inf_obj.language_info["init_prompt"]
                        self.prompt.add(init_prompt)
                functions.append(inf_obj.schema)
                # log.dbg(f"  no keywords attached to {inf_obj.name}, "
                #         "added schema")
                continue

            if keywords_in_input:
                if "init_prompt" in inf_obj.language_info:
                    if inf_obj.language_info["init_prompt"]:
                        init_prompt = inf_obj.language_info["init_prompt"]
                        self.prompt.add(init_prompt)
                functions.append(inf_obj.schema)
                log.dbg(f"  keywords detected {str(keywords_in_input)} "
                        f"for {inf_obj.name}, added schema")
                continue
            # else:
            #     log.dbg(f"  no keywords detected for {inf_obj.name}")

            if inf_obj.execute_count:
                log.dbg(f"  execute_count for {inf_obj.name} is "
                        f"{inf_obj.execute_count}, "
                        "added schema")
                inf_obj.execute_count -= 1
                functions.append(inf_obj.schema)
                continue

        tools = []

        for fct in functions:
            fct_dict = {
                "type": "function",
                "function": fct
            }
            tools.append(fct_dict)

        return tools, functions
