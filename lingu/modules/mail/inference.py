"""
Mail Inference Module

- responsible for offering the llm the ability to summarize emails,
  determine their importance and extract links from them.
- the llm fills out a pydantic data structure based
  on the provided prompt and content

"""

from lingu import Populatable, is_internal
from pydantic import BaseModel, Field
from .logic import logic
from typing import List


class RetrieveEmails(Populatable):
    """
    Retrieves the user emails.
    You can filter for only important emails and set a time frame to retrieve.
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
        description="Title of the Link. Extract a short, descriptive "
        "title for the link from the email's content."
    )
    url: str = Field(
        ...,
        description="URL of the Link"
    )


@is_internal()
class SummarizeEmail(Populatable):
    """
    Your task is to summarize the email content, determine its importance and
    extract the links contained in it.
    """
    summarized_content: str = Field(
        ...,
        description="Summarize the content of the email in your own words, "
        "very short (1-2 sentences)."
    )
    importance_mail: int = Field(
        ...,
        description="""
Judge the importance of this email based on its sender, urgency, relevance to
ongoing tasks or projects, and potential impact on work or personal life on a
scale from 0 to 10, where 10 is the most important. Consider the following
criteria:
- A score of 0-2 indicates non-urgent, non-relevant communication such as
  promotional emails or general newsletters.
- A score of 3-5 is for moderately important emails that may have some
  relevance but are not urgent.
- A score of 6-8 should be used for emails that are quite important,
  affecting ongoing projects or tasks significantly.
- A score of 9-10 is reserved for highly urgent and critical emails
  that require immediate attention and have a substantial impact.
"""
    )

    links: List[Link] = Field(
        ...,
        description="List of links contained in the email. "
    )
