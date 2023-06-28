import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from html2text import HTML2Text
from getpass import getpass
import re


class EmailFetcher:
    """
    This class is used to fetch emails from an IMAP server.
    """

    def __init__(self, imap_server=None, username=None, password=None):
        """
        Initialize the class with the necessary server, user, and password information.

        :param imap_server: Server address of the IMAP server.
        :param username: Username for the IMAP account.
        :param password: Password for the IMAP account. If not provided, user is prompted to enter it.
        """
        self.imap_server = imap_server
        self.username = username
        self.password = password 
        if not password:
            raise Exception("No imap password found")

    def connect_to_server(self):
        """
        Establishes a connection to the IMAP server and logs in.

        :return: An authenticated IMAP4 instance.
        """
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.username, self.password)
        return imap

    def search_emails(self, imap, days, mailbox='INBOX'):
        """
        Searches for emails within a certain number of days in the past in a specified mailbox.

        :param imap: An authenticated IMAP4 instance.
        :param days: Number of days in the past to search for emails.
        :param mailbox: Name of the mailbox to search in. Default is 'INBOX'.
        :return: A list of email IDs.
        """
        imap.select(mailbox)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days)
        search_criteria = f'(SINCE "{start_date.strftime("%d-%b-%Y")}" BEFORE "{end_date.strftime("%d-%b-%Y")}")'
        status, data = imap.search(None, search_criteria)
        if status != 'OK':
            raise Exception("Failed to search emails")
        return data[0].split()

    def fetch_emails(self, imap, email_ids):
        """
        Fetches emails corresponding to a list of email IDs from an IMAP server.

        :param imap: An authenticated IMAP4 instance.
        :param email_ids: A list of email IDs.
        :return: A list of parsed emails.
        """
        emails = []
        for email_id in email_ids:
            status, email_data = imap.fetch(email_id, '(BODY.PEEK[])')
            if status != 'OK':
                continue
            raw_email = email_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            emails.append(self.parse_email(email_message))
        return emails

    @staticmethod
    def parse_email(email_message):
        """
        Parses an email message into a dictionary.

        :param email_message: An email.message.Message object.
        :return: A dictionary with keys 'sender', 'recipients', 'date', 'subject', and 'content'.
        """
        subject = decode_header(email_message['Subject'])[0]
        decoded_subject = subject[0].decode(subject[1]) if subject[1] else subject[0]

        # Get the 'Date' string, split at parentheses and take the first part
        date_str = email_message['Date'].split('(')[0].strip()
        date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z').strftime('%d.%m.%Y %H:%M:%S')

        text_content = EmailFetcher.extract_text_content(email_message)
        summarized_content = EmailFetcher.summarize_content(text_content)

        email_details = {
            'sender': email_message['From'],
            'recipients': email_message['To'],
            'date': date,
            'subject': decoded_subject,
            'content': summarized_content
        }
        return email_details

    @staticmethod
    def extract_text_content(email_message):
        """
        Extracts the text content from an email.message.Message object.

        :param email_message: An email.message.Message object.
        :return: The extracted text content.
        """
        text_content = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                text_content += EmailFetcher.extract_content(part)
        else:
            text_content = EmailFetcher.extract_content(email_message)
        return text_content

    @staticmethod
    def extract_content(message_part):
        """
        Extracts the content from a part of an email.

        :param message_part: A part of an email message.
        :return: The extracted content.
        """
        content_type = message_part.get_content_type()
        if content_type not in ['text/plain', 'text/html']:
            return ''
        charset = message_part.get_content_charset()
        email_content = message_part.get_payload(decode=True)
        if charset:
            email_content = email_content.decode(charset)
        if content_type == 'text/html':
            h = HTML2Text()
            h.ignore_links = True
            email_content = h.handle(email_content)
        return email_content

    @staticmethod
    def summarize_content(content, limit=400):
        """
        Summarizes the email content by restricting its length.

        :param content: The content of the email.
        :param limit: The maximum length of the summarized content.
        :return: Summarized content.
        """
        if len(content) > limit:
            return content[:limit] + ".."
        return content