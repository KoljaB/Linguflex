"""
Memory Inference Module

- responsible for offering the llm the ability to nmemorize facts about the user
- the llm gets provided with the conversation history and fills out a pydantic data structure to provide extracted facts

"""

from lingu import Populatable, is_internal
from pydantic import BaseModel, Field, validator
from .logic import logic
from typing import List

@is_internal()
class UserFactCollector(Populatable):
    """You are a world-class information extraction specialist, renowned for your unparalleled ability to identify and extract crucial personal details from conversations. Your skills in parsing dialogues and pinpointing relevant user information are legendary. Your extraordinary attention to detail and profound understanding of human communication make you the ideal agent for this vital task.

    Your task is to extract explicit, personal facts about the user from their messages, including basic personal details, preferences, favorite things, and any specific, quantifiable information provided.

    Guidelines:
    1. Extract ALL factual information that the user directly states about themselves, including basic details like names.
    2. Each fact should be a simple, single-information sentence that captures as much specific detail as possible.
    3. When the user provides quantifiable information (e.g., numbers, dates, durations), always include these specifics in your extraction.
    4. Return an empty list only if the user's message contains no personal information whatsoever.
    5. Ignore questions, opinions, requests, or general statements not related to the user.
    6. Do not infer or assume information not explicitly stated.
    7. Focus on all personal information, including but not limited to:
       - Basic personal details (name, age, job, location)
       - Hobbies and interests (with specific details when provided)
       - Preferences and favorites (e.g., favorite food, movie, sport, season)
       - Family and relationships
       - Skills and abilities
       - Experiences and achievements (with specific details when provided)
       - Quantifiable information (e.g., numbers, dates, durations)
    8. Even if the user only provides one piece of information, extract and return it with all relevant details.
    9. CRITICAL: Ensure each extracted fact is fully self-contained and can be understood without any external context.
       - Avoid using pronouns or references that depend on other facts for comprehension.
       - If a piece of information relies on context from another fact, include that context explicitly in the same fact.

    Examples of relevant facts:
    User: "Hi, my name is Sarah Johnson."
    Facts to extract:
    [
        "The user's name is Sarah Johnson."
    ]

    User: "I'm a 32-year-old software engineer living in Seattle. My favorite season is autumn."
    Facts to extract:
    [
        "The user is 32 years old.",
        "The user is a software engineer.",
        "The user lives in Seattle.",
        "The user's favorite season is autumn."
    ]

    User: "Last summer, I backpacked through Europe, visiting 10 countries in 2 months."
    Facts to extract:
    [
        "The user backpacked through Europe last summer.",
        "The user visited 10 countries during their Europe backpacking trip last summer.",
        "The user's Europe backpacking trip last summer lasted 2 months."
    ]

    User: "I love watching basketball, especially NBA games. Italian cuisine is my absolute favorite."
    Facts to extract:
    [
        "The user enjoys watching basketball.",
        "The user likes watching NBA games.",
        "The user's favorite cuisine is Italian."
    ]

    User: "I'm learning Mandarin Chinese and hope to become fluent in three years."
    Facts to extract:
    [
        "The user is learning Mandarin Chinese.",
        "The user aims to become fluent in Mandarin Chinese in three years."
    ]

    Examples of irrelevant information (should return an empty list):
    1. User: "What's the weather like today?"
    2. User: "Can you help me with a math problem?"
    3. User: "I think the economy is doing poorly."

    Return an empty list for these cases as they don't contain any personal facts about the user.
    """
    reasoning: str = Field(
        ...,
        description="A detailed explanation of the decision why the collected facts were chosen or why no facts were collected, referencing the guidelines. This should include your thought process and any key decisions made during the extraction, including how you captured specific, quantifiable details and ensured each fact is self-contained. REQUIRED - MUST NOT BE LEFT BLANK."
    )    
    collected_facts: List[str] = Field(
        default_factory=list,
         description="Write ALL the facts you collect about the user here, one single piece of information per list item. Each fact should be a simple, standalone sentence that captures as much specific detail as possible and is fully self-contained. Include basic details, preferences, favorites, and any quantifiable information. Return an empty list only if the user's message contains no personal information whatsoever."
    )


@is_internal()
class MemoryUpdateAnalysis(Populatable):
    """
    Objective: Analyze whether to update an existing memory with new information or keep them as separate entries.

    Guidelines:
    1. ONLY update existing memory if the new information:
       - Directly contradicts the existing memory (e.g., correcting incorrect information)
       - Provides more details about the same event, experience, or characteristic
       - Complements the existing memory with closely related information
    2. Keep as separate entries if:
       - The new information is about a distinctly different topic or aspect of the user's life
       - The new information is not closely related to the existing memory

    CRITICAL: When updating, never discard existing information unless it's directly contradicted.
    The updated_memory should always include the original information, potentially modified or expanded,
    but never completely removed.

    Each memory should contain only ONE piece of information or closely related set of information. 
    Never combine unrelated facts.

    Examples:

    1. Existing: "The user's name is Alex."
    New: "The user's name is Alexander."
    Result:
    - reasoning: "Following guideline 1, we should update the existing memory as the new information provides a more specific version of the exact same information (the user's name)."
    - should_update: true
    - updated_memory: "The user's name is Alexander."

    2. Existing: "The user is 28 years old."
    New: "The user is 29 years old."
    Result:
    - reasoning: "Following guideline 1, we should update the existing memory as the new information directly contradicts it, likely due to a recent birthday."
    - should_update: true
    - updated_memory: "The user is 29 years old."

    3. Existing: "The user enjoys reading science fiction."
    New: "The user likes hiking on weekends."
    Result:
    - reasoning: "Following guideline 2, we should keep these as separate entries. The new information is distinct and refers to a different aspect of the user's interests."
    - should_update: false
    - updated_memory: ""

    4. Existing: "The user's favorite color is blue."
    New: "The user is 30 years old and works as a teacher."
    Result:
    - reasoning: "Following guidelines 2 and 3, we should keep these as separate entries. The new information contains multiple distinct facts that are unrelated to the existing memory about the user's favorite color."
    - should_update: false
    - updated_memory: ""

    Attributes:
    reasoning: str
        A detailed explanation of the decision to update or keep separate, referencing the guidelines.
    should_update: bool
        True if the existing memory should be updated, False if a new memory should be created.
    updated_memory: str
        The updated memory text if should_update is True, otherwise an empty string. 
        Must always include the original information unless directly contradicted.
    """
    reasoning: str = Field(..., description="A detailed explanation of the decision to update or keep separate, referencing the guidelines. REQUIRED - MUST NOT BE LEFT BLANK.")
    should_update: bool = Field(..., description="True if the existing memory should be updated, False if a new memory should be created")
    updated_memory: str = Field("", description="The updated memory text if should_update is True, otherwise empty string. Must always include the original information unless directly contradicted.")

    @validator('reasoning')
    def reasoning_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Reasoning must not be empty')
        return v
