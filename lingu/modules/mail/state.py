from lingu import cfg, State
from datetime import datetime, timedelta

history_hours = int(cfg("mail", "history_hours", default=24))


class MailState(State):
    def __init__(self):
        super().__init__()
        self.large_symbol = "📪"
        self.processed_mails = []
        self.mails = []
        self.last_fetch_time = None

    def format_duration(self, seconds):
        # Calculate hours, minutes and seconds
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        s = int(s)
        m = int(m)
        h = int(h)

        if h:
            return f"{h}'"
        else:
            return f"{m}\""

    def process_state(self):

        # Get current date and time
        now = datetime.now()

        # Filter mails older than 3 days
        self.mails = [
            mail for mail in self.mails
            if now - datetime.strptime(mail['date'], '%d.%m.%Y %H:%M:%S')
            <= timedelta(hours=history_hours)
        ]
        self.processed_mails = [
            mail for mail in self.processed_mails
            if now - datetime.strptime(mail['date'], '%d.%m.%Y %H:%M:%S')
            <= timedelta(hours=history_hours)
        ]

        if len(self.processed_mails) > 0:
            self.large_symbol = "📫"
            self.bottom_info = f"{len(state.mails)}"
            first_mail = state.mails[0]
            first_mail_date = first_mail['date']
            first_mail_date_obj = datetime.strptime(
                first_mail_date,
                '%d.%m.%Y %H:%M:%S'
            )
            seconds_since_first_mail = \
                (datetime.today() - first_mail_date_obj).total_seconds()
            self.top_info = self.format_duration(seconds_since_first_mail)
        else:
            self.large_symbol = "📪"
            self.bottom_info = ""
            self.top_info = ""


state = MailState()
