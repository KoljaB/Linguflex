from lingu import Invokable

symbol = "🐪"

@Invokable
def get_camel_fact():
    "Call immediately when camels come up."

    return "Contrary to popular belief, camels do not store water in their humps. Their humps actually store fat, which can be converted into water and energy."