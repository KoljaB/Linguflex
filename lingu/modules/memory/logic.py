from lingu import log, prompt, Logic, notify
from .state import state
import time
import threading
from .handlers.memory import Memory
from colorama import Fore, Style

potential_existing_memory_threshold = 0.4
debug = True

class MemoryLogic(Logic):
    def __init__(self):
        super().__init__()

        self.memory_dir = "memory_data"        
        self.memory = Memory(save_dir=self.memory_dir)
        self.processing = False

        self.add_listener(
            "before_user_text_complete",
            "listen",
            self.on_before_user_text_complete)        

        self.add_listener(
            "user_text_complete",
            "listen",
            self.on_user_text_complete)        

        self.add_listener(
            "assistant_text_complete",
            "brain",
            self.on_assistant_answer)        

        self.add_listener(
            "history_serve",
            "brain",
            self.on_history)
        
        self.user_text = ""

    def init(self):
        self.ready()

    def on_user_text_complete(self, user_text):
        self.processing = True
        self.user_text = user_text

    def on_before_user_text_complete(self, user_text):
        self.processing = True
        self.user_text = user_text

        related_memories = self.memory.search(user_text, user_id="core", k=5)

        # prompt
        memories = []
        for mem, combined_score, semantic_similarity, tfidf_similarity in related_memories:
            if combined_score > potential_existing_memory_threshold:
                memories.append(mem["text"])
                log.inf(f'  - add memory to context: {Fore.YELLOW}{mem["text"]}{Style.RESET_ALL}')
        
        if len(memories):
            prompt_string = "Consider this contextual information when relevant (extracted facts about the user):\n" + "\n".join(memories)
            
            log.inf(f"Adding to prompt: {prompt_string}")
            prompt.pre_add(prompt_string)

    def on_assistant_answer(self, assistant_text):
        self.trigger("history_request")

    def should_update_memory(self, existing_memory, new_memory):

        prompt = f"""Analyze whether to update the existing memory with new information or keep them as separate entries.
Follow these guidelines strictly:

1. ONLY update existing memory if the new information:
   - Directly contradicts the existing memory (e.g., correcting incorrect information)
   - Provides more details about the same event, experience, or characteristic
   - Complements the existing memory with closely related information

2. Keep as separate entries if:
   - The new information is about a distinctly different topic or aspect of the user's life
   - The new information is not closely related to the existing memory

3. CRITICAL: When updating, never discard existing information unless it's directly contradicted.
   The updated_memory must always include the original information, potentially modified or expanded,
   but never completely removed.

4. Each memory should contain only ONE piece of information or closely related set of information. 
   Never combine unrelated facts.

5. If in doubt about whether information is closely related, keep it as a separate entry.

Provide a detailed analysis in the following format:
- reasoning: [Your detailed explanation, referencing the guidelines]
- should_update: [true/false]
- updated_memory: [The updated memory text if should_update is true, otherwise empty string. Must always include the original information unless directly contradicted.]

Examples:

1. Existing: "The user's name is Alex."
   New: "The user's name is Alexander."
   Result:
   - reasoning: "Following guideline 1, we should update the existing memory as the new information provides a more specific version of the exact same information (the user's name). This directly contradicts the existing information."
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
   - reasoning: "Following guidelines 2 and 4, we should keep these as separate entries. The new information contains multiple distinct facts that are unrelated to the existing memory about the user's favorite color."
   - should_update: false
   - updated_memory: ""

5. Existing: "The user works as a software engineer."
   New: "The user has been promoted to senior software engineer."
   Result:
   - reasoning: "Following guidelines 1 and 3, we should update the existing memory. The new information provides more details about the same aspect of the user's life (their job). Importantly, we're not discarding the original information, but enhancing it."
   - should_update: true
   - updated_memory: "The user works as a senior software engineer, having been promoted from their previous position."

6. Existing: "The user's name is Alice Johnson."
   New: "The user is 28 years old and works as a software engineer."
   Result:
   - reasoning: "Following guidelines 2 and 4, we should keep these as separate entries. The new information contains distinct facts about the user's age and occupation, which are unrelated to the existing memory about the user's name. We must not discard or overwrite the existing name information."
   - should_update: false
   - updated_memory: ""

Now, analyze the following:

Existing memory: "{existing_memory}"
New information: "{new_memory}"
"""

        result = self.inference_safe(
            "MemoryUpdateAnalysis",
            prompt,
            "Analyze whether to update the existing memory with the new information or keep them separate.",
            model="ollama")

        return result


    def process_history(self, history):
        while history and history[-1]['role'] == 'assistant':
            history.pop()

        extract_prompt = f"""You are an exceptional information extraction specialist, renowned for your ability to identify and extract crucial personal details from conversations. Your skills in parsing dialogues and pinpointing relevant user information are unparalleled. Your meticulous attention to detail and comprehensive understanding of human communication make you the perfect agent for this critical task.

Your mission is to extract ALL explicit personal facts about the user from their messages, including basic personal details, information about their life, environment, relationships, their preferences and favorite things, and any specific, quantifiable information provided.

Here is the conversation history for context:
{history}

Extract explicit personal facts about the user from their last message, including ALL information about their life, environment, relationships, favorites, and any specific details or quantities mentioned.
Follow these guidelines:
1. Extract ALL factual information that the user directly states about themselves or their immediate sphere of influence, including basic details like names.
2. Each extracted fact should be as specific and detailed as the user's statement allows. Capture quantifiable information whenever possible.
3. Consider a wide range of personal information, including but not limited to:
   - Basic personal details (name, age, occupation, location)
   - Family and relationships
   - Pets and animals in their care
   - Hobbies and interests (with specific details when provided)
   - Possessions or belongings of significance
   - Daily routines or habits
   - Skills or abilities
   - Personal preferences or dislikes
   - Favorite things (e.g., favorite food, movie, sport, season, holiday)
   - Experiences and achievements (with specific details when provided)
   - Quantifiable information (e.g., numbers, dates, durations)
4. Ignore questions, opinions, or general statements not related to the user's personal life.
5. Do not infer or assume information not explicitly stated.
6. Return an empty list ONLY if there are absolutely no extractable personal facts about the user.
7. Pay special attention to statements about preferences or favorites, and include these in your extraction.
8. When the user provides numerical data or specific timeframes, always include these in your extracted facts.
9. Even if the user only provides one piece of information (e.g., just their name), extract and return it with all relevant details.
10. CRITICAL: Ensure each extracted fact is fully self-contained and can be understood without any external context.
    - Avoid using pronouns or references that depend on other facts for comprehension.
    - If a piece of information relies on context from another fact, include that context explicitly in the same fact.
    - Each fact should be independently understandable and queryable.

Examples:

1. Input: "Hi, my name is John Smith."
   Result:
   - reasoning: "The user has provided their full name, which is a single, specific piece of information about their identity."
   - collected_facts: ["The user's name is John Smith."]

2. Input: "I work as a high school teacher and I've been trying to learn classical guitar for the past 6 months. My favorite movie is The Shawshank Redemption."
   Result:
   - reasoning: "The user has provided multiple distinct facts about their occupation, hobby, and preferences. Each of these should be extracted as separate, self-contained pieces of information."
   - collected_facts: [
       "The user works as a high school teacher.",
       "The user has been learning classical guitar for 6 months.",
       "The user's favorite movie is The Shawshank Redemption."
     ]

3. Input: "Last summer, I backpacked through Europe, visiting 10 countries in 2 months."
   Result:
   - reasoning: "The user has shared information about a past travel experience, including specific details about the duration and scope of the trip. These details should be extracted as separate, self-contained facts."
   - collected_facts: [
       "The user backpacked through Europe last summer.",
       "The user visited 10 countries during their Europe backpacking trip last summer.",
       "The user's Europe backpacking trip last summer lasted 2 months."
     ]

4. Input: "I love Italian cuisine, especially homemade pasta dishes. Basketball is my favorite sport to watch, particularly NBA games."
   Result:
   - reasoning: "The user has provided information about their food preferences and sports interests. These should be extracted as separate, self-contained facts, with more specific details included where provided."
   - collected_facts: [
       "The user loves Italian cuisine.",
       "The user especially enjoys homemade pasta dishes.",
       "The user's favorite sport to watch is basketball.",
       "The user particularly enjoys watching NBA games."
     ]

5. Input: "I'm 32 years old, married, and have two kids. We live in a small house in Seattle with our golden retriever, Max."
   Result:
   - reasoning: "The user has shared multiple pieces of personal information about their age, family status, location, and pet. Each of these should be extracted as separate, self-contained facts."
   - collected_facts: [
       "The user is 32 years old.",
       "The user is married.",
       "The user has two kids.",
       "The user lives in Seattle.",
       "The user lives in a small house.",
       "The user has a golden retriever named Max."
     ]

6. Input: "I graduated from MIT with a degree in Computer Science five years ago. Now I'm working on my PhD in AI at Stanford."
   Result:
   - reasoning: "The user has provided information about their educational background, including past and current studies. These should be extracted as separate, specific, and self-contained facts."
   - collected_facts: [
       "The user graduated from MIT.",
       "The user has a degree in Computer Science from MIT.",
       "The user graduated from MIT five years ago.",
       "The user is currently working on a PhD.",
       "The user is currently working on a PhD in AI.",
       "The user is currently studying at Stanford for their PhD in AI."
     ]

7. Input: "I'm learning Mandarin Chinese and hope to become fluent in three years."
   Result:
   - reasoning: "The user has shared information about a language learning goal with a specific timeframe. This should be extracted as two separate, self-contained facts."
   - collected_facts: [
       "The user is learning Mandarin Chinese.",
       "The user aims to become fluent in Mandarin Chinese in three years."
     ]

Example of irrelevant information (should return an empty list):
User: "What's the capital of France?"
Facts to extract: []
"""

        while not self.inference_manager.inference_allowed:
            log.inf("Process history, waiting for inference_allowed")
            time.sleep(0.1)
        
        log.inf (f"Extract prompt:\n{extract_prompt}")
        log.inf (f"Last user message: {self.user_text}")

        result = self.inference_safe(
            "UserFactCollector",
            extract_prompt,
            f"Last user message: {self.user_text}",
            "ollama")

        if result and len(result.collected_facts):
            log.inf(f"Memory information was extracted, reason: {result.reasoning}")
            for frag in result.collected_facts:
                log.inf(f"Result extraction: {frag}")

                related_memories = self.memory.search(frag, user_id="core", k=3)

                updated = False
                for mem, combined_score, semantic_similarity, tfidf_similarity in related_memories:
                    if combined_score > potential_existing_memory_threshold:
                        log.inf(f"Existing memory score ({combined_score:.1f}) is over threshold {potential_existing_memory_threshold:.1f}")                    
                        decision = self.should_update_memory(mem['text'], frag)
                        if decision.should_update and len(decision.updated_memory):
                            log.inf("Updating memory")
                            log.inf("Reason:\n", decision.reasoning)
                            log.inf(f'  - OLD: {Fore.GREEN}{mem["text"]}{Style.RESET_ALL}')
                            log.inf(f'  - NEW: {Fore.GREEN}{decision.updated_memory}{Style.RESET_ALL}')
                            notify("Updated memory", f'from: {mem["text"]}\nto: {decision.updated_memory}', -1, "custom", "💭")

                            self.memory.remove(mem['text'])
                            self.memory.add(decision.updated_memory, user_id="core")
                            updated = True
                            break
                        elif decision.should_update:
                            if debug:
                                log.inf(f"!!! should_update TRUE BUT NO updated_memory TEXT PROVIDED!!! (that should not occur => validator!)")
                        else:
                            if debug:
                                log.inf("Don't update, keeping memories separate")
                                log.inf("Reason:\n", decision.reasoning)
                if not updated:
                    log.inf(f'  - added new core memory: {Fore.GREEN}{frag}{Style.RESET_ALL}')
                    result = self.memory.add(frag, user_id="core")
                    notify("New memory", f'{frag}', -1, "custom", "💭")
            
            self.memory.save()
        elif result is None:
            log.inf("  - nothing submitted")
        else:
            log.inf(f"  - no information could be extracted (reason: {result.reasoning})")
        self.processing = False

    def on_history(self, history):

        log.dbg(f"Memory current history: {history}")
        
        thread = threading.Thread(target=self.process_history, args=(history,))
        thread.start()

    def wait_memory(self):
        while self.processing:
            time.sleep(0.01)


logic = MemoryLogic()
