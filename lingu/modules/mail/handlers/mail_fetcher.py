from datetime import datetime, timedelta
from email.header import decode_header
from dateutil.parser import parse
from html2text import HTML2Text
from bs4 import BeautifulSoup
import imaplib
from lingu import log
import email


class MailFetcher:
    """
    This class is used to fetch emails from an IMAP server.
    """

    def __init__(self, imap_server=None, username=None, password=None):
        """
        Initialize the class with the necessary server, user,
        and password information.

        :param imap_server: Server address of the IMAP server.
        :param username: Username for the IMAP account.
        :param password: Password for the IMAP account.
          If not provided, user is prompted to enter it.
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

    def search_emails(self, imap, hours=24, mailbox='INBOX'):
        """
        Searches for emails within a certain number of days
        in the past in a specified mailbox.

        :param imap: An authenticated IMAP4 instance.
        :param days: Number of days in the past to search for emails.
        :param mailbox: Name of the mailbox to search in. Default is 'INBOX'.
        :return: A list of email IDs.
        """
        imap.select(mailbox)

        start_date_naive = datetime.now() - timedelta(hours=hours)
        start_date = start_date_naive.astimezone()
        end_date_naive = datetime.now() + timedelta(days=1)
        end_date = end_date_naive.astimezone()

        search_criteria = (
            f'(SINCE "{start_date.strftime("%d-%b-%Y")}" '
            f'BEFORE "{end_date.strftime("%d-%b-%Y")}")'
        )

        log.dbg(f"  [mails] search criteria: {search_criteria}")

        status, data = imap.search(None, search_criteria)
        print(
            f"found {len(data[0].split())} mails "
            f"between {start_date} and {end_date}"
        )
        if status != 'OK':
            raise Exception("Failed to search emails")
        return data[0].split()

    def fetch_emails(self, imap, email_ids, hours=24):
        """
        Fetches emails corresponding to a list of email IDs
          from an IMAP server.

        :param imap: An authenticated IMAP4 instance.
        :param email_ids: A list of email IDs.
        :return: A list of parsed emails.
        """

        start_date_naive = datetime.now() - timedelta(hours=hours)
        start_date = start_date_naive.astimezone()

        emails = []
        for email_id in email_ids:
            status, email_data = imap.fetch(email_id, '(BODY.PEEK[])')
            if status != 'OK':
                continue
            raw_email = email_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            parsed_mail = self.parse_email(email_message)
            email_date = parse(parsed_mail['raw_date'])

            if email_date < start_date:
                continue

            emails.append(parsed_mail)
        return emails

    @staticmethod
    def decode_mime_header(header_value):
        if header_value is None:
            return ''
        decoded_header = decode_header(header_value)
        header_parts = []
        for part, encoding in decoded_header:
            if encoding:
                part = part.decode(encoding)
            elif isinstance(part, bytes):
                part = part.decode('utf-8', errors='replace')
            header_parts.append(part)
        return ''.join(header_parts)

    @staticmethod
    def parse_email(email_message):
        """
        Parses an email message into a dictionary.

        :param email_message: An email.message.Message object.
        :return: A dictionary with keys 'sender', 'recipients', 'date',
          'subject', and 'content'.
        """
        subject = MailFetcher.decode_mime_header(email_message['Subject'])

        # Get the 'Date' string and parse it with dateutil
        date_str = email_message['Date'].split('(')[0].strip()
        raw_date = parse(date_str)
        raw_date_iso = raw_date.isoformat()
        date = raw_date.strftime('%d.%m.%Y %H:%M:%S')

        content_text, content_html = MailFetcher.extract_text_content(
            email_message)
        summarized_content = MailFetcher.summarize_content(content_text)

        email_details = {
            'sender': email_message['From'],
            'recipients': email_message['To'],
            'date': date,
            'raw_date': raw_date_iso,
            'subject': subject,
            'content_html': content_html,
            'content_text': content_text,
            'summary': summarized_content
        }
        return email_details

    @staticmethod
    def extract_text_content(email_message):
        """
        Extracts the text content from an email.message.Message object.

        :param email_message: An email.message.Message object.
        :return: The extracted text content.
        """
        content_text = ""
        content_html = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                txt, email = MailFetcher.extract_content(part)
                content_text += txt
                content_html += email
        else:
            txt, email = MailFetcher.extract_content(email_message)
            content_text = txt
            content_html = email
        return content_text, content_html

    @staticmethod
    def extract_text_preserve_links(html_content):
        """
        Extracts text from HTML content and preserves hyperlink
          using Beautiful Soup.

        Args:
        html_content (str): A string containing HTML content.

        Returns:
        str: Extracted text content with preserved hyperlinks.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        text_with_links = []

        for element in soup.recursiveChildGenerator():
            if element.name == 'a' and element.get('href', None):
                link_text = element.text.strip()
                link_url = element['href']
                text_with_links.append(f"[{link_text}]({link_url})")
            # if it's a navigable string and not a tag
            elif element.name is None:
                text_with_links.append(element.strip())

        return ' '.join(text_with_links)

    @staticmethod
    def get_text_from_html(html):
        h = HTML2Text()
        h.single_line_break = False
        # h.body_width = 0
        h.ignore_links = False
        content_text = h.handle(html)
        return content_text

    @staticmethod
    def extract_content(message_part):
        content_type = message_part.get_content_type()
        charset = message_part.get_content_charset() or 'utf-8'
        content = message_part.get_payload(decode=True)

        # Check if content is None
        if content is None:
            return '', ''

        # Handling possible decoding errors
        try:
            content = content.decode(charset)
        except UnicodeDecodeError:
            try:
                # Attempt decoding with a different charset
                # if the first attempt fails
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                # If decoding still fails, replace problematic characters
                content = content.decode(charset, errors='replace')

        # Differentiate between text and HTML content
        content_text = content_html = content
        if content_type == 'text/html':
            content_text = MailFetcher.get_text_from_html(content)
        elif content_type != 'text/plain':
            content_text = ''  # Clear text content for non-text/plain parts

        return content_text, content_html

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
