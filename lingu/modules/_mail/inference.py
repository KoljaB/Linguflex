"""
House / Smart Home Module

- responsible for turning devices on and off and setting colors of bulbs

"""

from lingu import Populatable, is_internal
from pydantic import BaseModel, Field
from .logic import logic
from typing import List


class RetrieveEmails(Populatable):
    """
    Your task is to summarize the email content, determine its importance and
    extract the links contained in it.
    """
    only_important: bool = Field(
        default=True,
        description="Retrieve only important emails"
    )
    last_hours: int = Field(
        default=24,
        description="Retrieve emails from the last x hours"
    )

    def on_populated(self):
        return logic.return_emails(self.only_important, self.last_hours)


class Link(BaseModel):
    "Represents a link contained in an email."
    name: str = Field(
        ...,
        description="Title of the Link. Extract a short, descriptive title for the link from the email's content."
    )
    url: str = Field(
        ...,
        description="URL of the Link"
    )
#     importance: int = Field(
#         ...,
#         description="""
# Judge the importance of this link based on its relevance to the email's content, the trustworthiness of the sender, and the context in which it is presented on a scale from 0 to 10, where 10 is the most important. Consider the following criteria:
# - A score of 0-2 is for links that are not relevant to the email's content, come from unverified or suspicious senders, or are presented in a promotional or unrelated context.
# - A score of 3-5 should be given to links that have moderate relevance to the email, come from somewhat reliable sources, or are presented in a somewhat relevant context.
# - A score of 6-8 is for links that are quite relevant to the email's content, come from trustworthy sources, and are presented in a context that aligns well with the email's purpose.
# - A score of 9-10 is reserved for highly relevant links that are essential to the email's content, come from highly trustworthy sources, and are presented in a context that is critically important for understanding or acting on the email's message.

# Please provide a brief summary of the link and rate its importance based on these criteria.
# """
#     )


@is_internal()
class SummarizeEmail(Populatable):
    """
    Your task is to summarize the email content, determine its importance and
    extract the links contained in it.
    """
    summarized_content: str = Field(
        ...,
        description="Summarize the content of the email in your own words, very short (1-2 sentences)."
    )
    importance_mail: int = Field(
        ...,
        description="""
Judge the importance of this email based on its sender, urgency, relevance to ongoing tasks or projects, and potential impact on work or personal life on a scale from 0 to 10, where 10 is the most important. Consider the following criteria:
- A score of 0-2 indicates non-urgent, non-relevant communication such as promotional emails or general newsletters.
- A score of 3-5 is for moderately important emails that may have some relevance but are not urgent.
- A score of 6-8 should be used for emails that are quite important, affecting ongoing projects or tasks significantly.
- A score of 9-10 is reserved for highly urgent and critical emails that require immediate attention and have a substantial impact.
"""
    )

    links: List[Link] = Field(
        ...,
        description="List of links contained in the email. "
    )












    # def on_populated(self):
    #     result = {}
    #     # for bulb in self.bulbs:
    #     #     if bulb.name in logic.get_bulb_names():
    #     #         log.dbg(f'  [lights] {bulb.name} to {bulb.color}')
    #     #         result[bulb.name] = logic.set_color_hex(bulb.name, bulb.color)
    #     #     else:
    #     #         log.dbg(f'  [lights] {bulb.name} not found {bulb.color}')
    #     #         result[bulb.name] = {
    #     #             "result": "error",
    #     #             "reason": f"bulb name {bulb.name} not found, "
    #     #                       "must be one of these: "
    #     #                       f"{logic.get_bulb_names_string()}",
    #     #         }

    #     # logic.colors_changed()
    #     return result


        # description="Judge the importance of this email based on its sender, urgency, relevance to ongoing tasks or projects, and potential impact on work or personal life on a scale from 0 to 10, where 10 is the most important."
