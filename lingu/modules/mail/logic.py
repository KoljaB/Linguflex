from .handlers.mail_fetcher import MailFetcher
from lingu import cfg, exc, log, Logic, repeat, notify
from dateutil.parser import parse
from datetime import datetime, timedelta
from threading import Thread
from .state import state
import pytz

MAIL_CHECK_INTERVAL_SECONDS = 300

imap_server = cfg("mail", "server")
user_name = cfg("mail", "username")
password = cfg("mail", "password")
history_hours = int(cfg("mail", "history_hours", default=24))
max_mail_length = int(cfg("mail", "max_mail_length", default=20000))
summary_prompt = cfg(
    "mail",
    "summary_prompt",
    default="Summarize this email content.")
importance_threshold = int(cfg("mail", "importance_threshold", default=5))
summarize_model = cfg("mail", "summarize_model", default="gpt-3.5-turbo-1106")


class MailLogic(Logic):
    """
    Logic class for handling email fetching, processing, and summarizing.

    Attributes:
        thread_started (bool): Indicates if the processing thread
          has been started.
        fetcher (MailFetcher): Instance of MailFetcher to interact
          with the email server.
    """
    def init(self):
        """Initializes the MailLogic class."""
        self.thread_started = False
        self.fetcher = None
        if not imap_server or not user_name or not password:
            log.err(
                "[mail] Missing IMAP server, username, or password.\n"
                "  Please open the 'settings.yaml' file and provide "
                "these data.")
            self.state.set_disabled(True)
        else:
            try:
                self.fetcher = MailFetcher(imap_server, user_name, password)
            except Exception as e:
                log.err(
                    f"[mail] Initialization failed: {e}\n"
                    "  Please open the 'settings.yaml' file and verify your "
                    "server, username and pw data.\n"
                    "  Check if the IMAP server is accessible.")
                self.fetcher = None
                self.state.set_disabled(True)

        self.ready()

    def return_emails(
            self,
            only_important: bool = True,
            last_hours: int = 24,
            debug=False
    ) -> list:
        """
        Filters and returns emails based on importance and time frame.

        Args:
            only_important (bool): If True, only returns important emails.
            last_hours (int): The time frame in hours to consider for emails.
            debug (bool): If True, provides additional debug information.

        Returns:
            list: A list of filtered email details.
        """
        mails = state.processed_mails

        # filter for last x hou
        if debug:
            log.dbg(f"  [mail] filtering mails for last {last_hours} hours")

        aware_current_time = (
            pytz.utc.localize(datetime.today()) - timedelta(hours=last_hours)
        )
        mails = [mail for mail in mails if
                 parse(mail["raw_date"]) > aware_current_time]

        if debug:
            log.dbg("  [mail] Time filtered mails (aware_current_time: "
                    f"{aware_current_time}): ", mails)
        if only_important:
            mails = [
                mail for mail in mails
                if mail["importance"] >= importance_threshold
            ]

            # sort mails by importance
            mails.sort(key=lambda mail: mail["importance"], reverse=True)

        if debug:
            log.dbg("  [mail] Importance filtered mails: ", mails)

        ret_mail = []
        for mail in mails:
            ret_mail.append({
                "subject": mail["subject"],
                "sender": mail["sender"],
                "date": parse(mail["raw_date"]).isoformat(),
                "content summary": mail["summary"],
                "importance": mail["importance"],
            })

        if debug:
            log.dbg("  [mail] Returned filtered mails: ", ret_mail)

        return ret_mail

    def fetch_email(self, mailbox='INBOX') -> None:
        """
        Fetches emails from the specified mailbox and processes them.

        Args:
            mailbox (str): The mailbox from which to fetch emails.
        """

        if not self.fetcher or state.is_disabled:
            log.dbg("  [mail] state is disabled, not fetching mails")
            return

        if state.last_fetch_time:
            last_fetch_time = datetime.fromisoformat(state.last_fetch_time)

            # calculate time difference
            time_diff = datetime.today() - last_fetch_time
            last_fetch = time_diff.total_seconds()

            check_again = MAIL_CHECK_INTERVAL_SECONDS - last_fetch
            if last_fetch < MAIL_CHECK_INTERVAL_SECONDS:
                log.inf("  [mail] no need to fetch mails, check again in "
                        f"{check_again} seconds")

                if not self.thread_started:
                    self.thread_started = True
                    Thread(target=self.process_state).start()
                return

        log.inf(f"  [mail] fetching mails from {mailbox} of {imap_server}")

        imap = self.fetcher.connect_to_server()
        email_ids = self.fetcher.search_emails(
            imap,
            history_hours,
            mailbox)
        mails = self.fetcher.fetch_emails(imap, email_ids, history_hours)
        mails.reverse()
        self.validate_mails(mails)
        imap.logout()

        state.mails = mails
        state.last_fetch_time = datetime.today().isoformat()

        state.save()

        if not self.thread_started:
            self.thread_started = True
            Thread(target=self.process_state).start()

    def process_state(self, debug=False) -> None:
        """
        Processes the fetched emails, performing summarization
          and importance evaluation.

        Args:
            debug (bool): If True, outputs additional debugging information.
        """
        mails_processed = 0

        for mail in state.mails:

            tries = 0
            if "tries" in mail:
                tries = mail["tries"]
            tries += 1
            mail["tries"] = tries
            date = mail["date"]
            sender = mail["sender"]
            subject = mail["subject"]
            content = mail["content_text"]

            # limit content size so llm doesnt get in context window probs
            content = content[:max_mail_length]
            raw_date = mail["raw_date"]

            if any(pm["sender"] == sender and pm["raw_date"] == raw_date
                   for pm in state.processed_mails):
                continue

            if tries > 3:
                state.save()
                continue

            try:
                result = self.inference(
                    "SummarizeEmail",
                    summary_prompt,
                    content,
                    summarize_model)
            except Exception as e:
                log.err(f"  [mail] error processing mail {subject}, "
                        f"exception {e}")
                exc(e)
                state.save()
                continue

            if result is None:
                log.wrn("  [mail] summarization inference returned no result "
                        f"for mail {subject}. Skipping summarization cycle.")
                tries -= 1
                mail["tries"] = tries
                state.save()
                break

            if debug:
                log.dbg(f"  [mail] summary result: {result}")

            links = []
            for link in result.links:
                links.append({
                    "name": link.name,
                    "url": link.url
                })

            if result.importance_mail is None:
                result.importance_mail = 0

            state.processed_mails.append({
                "subject": subject,
                "sender": sender,
                "raw_date": raw_date,
                "date": date,
                "content": content,
                "summary": result.summarized_content,
                "importance": result.importance_mail,
                "links": links
            })
            mails_processed += 1
            state.save()

        if mails_processed:
            notify(
                "Mails",
                f"You have {mails_processed} new emails",
                15000,
                "custom",
                "📫",
                "#808000")
        self.thread_started = False

    def validate_mails(self, mails) -> None:
        """
        Validates the mail items ensuring they are JSON serializable.

        Args:
            mails (list): The list of email data to validate.
        """
        import json
        problematic_items = []
        for mail in mails:
            for key, value in mail.items():
                try:
                    json.dumps(value)
                except TypeError:
                    problematic_items.append((key, value, mail["subject"]))

        if problematic_items:
            log.wrn("  [mail] found problematic items in state, not saving")
            for key, value, subject in problematic_items:
                log.wrn(f"  [mail] key: {key}, value: {value}, type: "
                        f"{type(value).__name__} in mail w subject {subject}")

    @repeat(60)
    def init_fetch_email(self):
        """Initializes and schedules the email fetching process."""
        if not self.fetcher or state.is_disabled:
            return

        self.fetch_email()
        state.process_state()


logic = MailLogic()
