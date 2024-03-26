"""
Module Template

- example module template for creating new modules

"""

from lingu import Populatable
# from pydantic import Field
from .logic import logic


class RetrieveCamelFact(Populatable):
    """
    Retrieves a fact about camels.
    """

    def on_populated(self):
        return logic.return_camel_fact()
