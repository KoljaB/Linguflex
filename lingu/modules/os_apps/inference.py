from lingu import log, Populatable
from pydantic import BaseModel, Field, validator
from .logic import logic
from typing import List

apps_list = logic.get_available_apps()

class open_os_app(Populatable):
    """
    Open an operating system application.

    Instructions:
    1. You MUST provide a valid application name in the app_name field.
    2. The app_name MUST be one of the allowed applications listed below.
    3. Do NOT leave app_name blank or set it to None.

    Example:
    app_name: "notepad"
    """
    app_name: str = Field(..., description=f"REQUIRED. Choose one app from: {apps_list}")

    @validator('app_name')
    def validate_app_name(cls, v):
        if not v or v.lower() == 'none':
            raise ValueError(f"app_name is required. Choose one from: {apps_list}")
        if v not in apps_list:
            raise ValueError(f"Invalid app_name. Must be one of: {apps_list}")
        return v

    def on_populated(self):
        result = {}
        if self.app_name in logic.get_available_apps():
            log.dbg(f'  [os_app] Opening {self.app_name}')
            result[self.app_name] = logic.open_os_app(self.app_name)
        else:
            if not self.app_name or self.app_name == "None":
                log.dbg(f'  [os_app] app_name not specified')
                raise ValueError(f"Write the app you want to call into app_name.")
            else:
                log.dbg(f'  [os_app] {self.app_name} not found')
                raise ValueError(f"App name {self.app_name} not found, "
                            "must be one of these: "
                            f"{', '.join(logic.get_available_apps())}")

        log.dbg(f'  [os_app] returning result to LLM: {result}')
        return result

        result = {}
        log.dbg(f'  [os_app] Opening {self.app_name}')
        result[self.app_name] = logic.open_os_app(self.app_name)
        log.dbg(f'  [os_app] returning result to LLM: {result}')
        return result


# """
# House / Smart Home Module

# - responsible for turning devices on and off and setting colors of bulbs

# """

# from lingu import log, Populatable
# from pydantic import BaseModel, Field
# from .logic import logic
# from typing import List

# apps_list = logic.get_available_apps()

# class open_os_app(Populatable):
#     """
#     The task is to open an operating system application. To do this, you need to:

#     1. ALWAYS provide the name of the application you want to open as app_name.
#     2. Ensure the application name is one of the allowed (permitted) applications.
#     3. The system will attempt to open the specified application if it's allowed.
#     """
#     #app_name: str
#     app_name: str = Field(..., description=f"Allowed applications are: {apps_list}")

#     def on_populated(self):
        
#         result = {}
#         if self.app_name in logic.get_available_apps():
#             log.dbg(f'  [os_app] Opening {self.app_name}')
#             result[self.app_name] = logic.open_os_app(self.app_name)
#         else:
#             if not self.app_name or self.app_name == "None":
#                 log.dbg(f'  [os_app] app_name not specified')
#                 raise ValueError(f"Write the app you want to call into app_name.")
#             else:
#                 log.dbg(f'  [os_app] {self.app_name} not found')
#                 raise ValueError(f"App name {self.app_name} not found, "
#                             "must be one of these: "
#                             f"{', '.join(logic.get_available_apps())}")

#         log.dbg(f'  [os_app] returning result to LLM: {result}')
#         return result
