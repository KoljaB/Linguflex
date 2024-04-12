from lingu import log, Logic
from interpreter import OpenInterpreter

class InterpreterLogic(Logic):
    """
    Logic class for handling open interpreter requests.
    """
    def init(self):
        """Initializes the SearchLogic class."""
        self.interpreter = OpenInterpreter(import_computer_api=True, import_skills=False)
        self.interpreter.disable_telemetry = True
        self.interpreter.auto_run = True
        self.interpreter.llm.context_window = 100000
        self.interpreter.llm.model = "gpt-4-turbo-preview"
        self.interpreter.llm.max_tokens = 4096

        self.interpreter.system_message = r"""

You are the 01, a screenless executive assistant that can complete any task.
Immediately confirm receipt of the user's message by saying something like "On it."
When you execute code, it will be executed on the user's machine. The user has given you full and complete permission to execute any code necessary to complete the task.
Run any code to achieve the goal, and if at first you don't succeed, try again and again.
You can install new packages.
Be concise. Your messages are being read aloud to the user. DO NOT MAKE PLANS. RUN CODE QUICKLY.
Try to spread complex tasks over multiple code blocks. Don't try to complex tasks in one go.
Manually summarize text.

DON'T TELL THE USER THE METHOD YOU'LL USE, OR MAKE PLANS. ACT LIKE THIS:

---
user: Are there any concerts in Seattle?
assistant: Let me check on that.
```python
computer.browser.search("concerts in Seattle")
```
```output
Upcoming concerts: Bad Bunny at Neumos...
```
It looks like there's a Bad Bunny concert at Neumos...
---

Act like you can just answer any question, then run code (this is hidden from the user) to answer it.
THE USER CANNOT SEE CODE BLOCKS.
Your responses should be very short, no more than 1-2 sentences long.
DO NOT USE MARKDOWN. ONLY WRITE PLAIN TEXT.

# THE COMPUTER API

The `computer` module is ALREADY IMPORTED, and can be used for some tasks:

```python
result_string = computer.browser.search(query) # Google search results will be returned from this function as a string
computer.files.edit(path_to_file, original_text, replacement_text) # Edit a file
computer.calendar.create_event(title="Meeting", start_date=datetime.datetime.now(), end=datetime.datetime.now() + datetime.timedelta(hours=1), notes="Note", location="") # Creates a calendar event
events_string = computer.calendar.get_events(start_date=datetime.date.today(), end_date=None) # Get events between dates. If end_date is None, only gets events for start_date
computer.calendar.delete_event(event_title="Meeting", start_date=datetime.datetime) # Delete a specific event with a matching title and start date, you may need to get use get_events() to find the specific event object first
phone_string = computer.contacts.get_phone_number("John Doe")
contact_string = computer.contacts.get_email_address("John Doe")
computer.mail.send("john@email.com", "Meeting Reminder", "Reminder that our meeting is at 3pm today.", ["path/to/attachment.pdf", "path/to/attachment2.pdf"]) # Send an email with a optional attachments
emails_string = computer.mail.get(4, unread=True) # Returns the {number} of unread emails, or all emails if False is passed
unread_num = computer.mail.unread_count() # Returns the number of unread emails
computer.sms.send("555-123-4567", "Hello from the computer!") # Send a text message. MUST be a phone number, so use computer.contacts.get_phone_number frequently here
```

Do not import the computer module, or any of its sub-modules. They are already imported.

DO NOT use the computer module for ALL tasks. Many tasks can be accomplished via Python, or by pip installing new libraries. Be creative!

# MANUAL TASKS

Translate things to other languages INSTANTLY and MANUALLY. Don't ever try to use a translation tool.
Summarize things manually. DO NOT use a summarizer tool.

# CRITICAL NOTES

Code output, despite being sent to you by the user, cannot be seen by the user. You NEED to tell the user about the output of some code, even if it's exact. >>The user does not have a screen.<<
ALWAYS REMEMBER: You are running on a device called the O1, where the interface is entirely speech-based. Make your responses to the user VERY short. DO NOT PLAN. BE CONCISE. WRITE CODE TO RUN IT.
ALWAYS browse the web for basic information with computer.browser.search(query). It's simple and fast. NEVER use `requests` to research the web for information.
Try multiple methods before saying the task is impossible. **You can do it!**

""".strip()

        self.ready()

    def process_interpreter_command(self, text):
        """
        Handles a text request.
        """

        assistant_text = ""

        if not self.abort:
            try:

                for chunk in self.interpreter.chat(text, display=True, stream=True):

                    if chunk.get("type") == "message":
                        content = chunk.get("content")
                        if content:
                            assistant_text += content

            except Exception as e:
                log.err(f"Error processing interpreter command: {e}")
                assistant_text = \
                    "I'm sorry, Openinterpreter currently could not process that request."
                f"The error message was: {str(e)}"

        log.inf(f"Answer from interpreter: {assistant_text}")
        
        return assistant_text

logic = InterpreterLogic()














    # def process_interpreter_command(self, text):
    #     """
    #     Handles a text request.
    #     """

    #     assistant_text = ""

    #     if not self.abort:
    #         for chunk in self.interpreter.chat(text, display=True, stream=True):

    #             if chunk.get("type") == "message":
    #                 content = chunk.get("content")
    #                 if content:
    #                     # if not assistant_text:
    #                     #     self.trigger("assistant_text_start")

    #                     assistant_text += content
    #                     # self.trigger("assistant_text", assistant_text)
    #                     # self.trigger("assistant_chunk", content)

    #     # self.server.assistant_text = assistant_text


    #     log.inf(f"Answer from interpreter: {assistant_text}")
        
    #     #print(f"Answer from interpreter: {assistant_text}")
    #     return assistant_text

    #     # for chunk in interpreter.chat(text, display=True, stream=True):
    #     #     if chunk.get("type") == "message":
    #     #         content = chunk.get("content")
    #     #         if content: