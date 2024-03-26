from lingu import Logic


class ModuleTemplateLogic(Logic):
    def return_camel_fact(self):
        return """
Contrary to popular belief, a camel's hump is not a reservoir for water.
Instead, it stores fat.
The camel can convert it into water and energy when food is scarce.
"""


logic = ModuleTemplateLogic()
