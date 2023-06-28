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

# import imaplib
# import email
# import datetime
# from email.header import decode_header
# import html2text
# import re
# import json

# class EmailFetcher:
#     """
#     Diese Klasse dient zum Abrufen von E-Mails von einem IMAP-Server.
#     """

#     def __init__(self, imap_server, username, password):
#         """
#         Initialisiert die Klasse mit den notwendigen Server-, Benutzer- und Passwortinformationen.
#         """
#         self.imap_server = imap_server
#         self.username = username
#         self.password = password

#     def get_mails(self, days):
#         """
#         Abrufen von E-Mails von 'days' Tagen in die Vergangenheit.
#         """
#         # Verbindung zum IMAP-Server herstellen
#         imap = imaplib.IMAP4_SSL(self.imap_server)
#         imap.login(self.username, self.password)

#         # Postfach auswählen (Standard-Ordner "INBOX")
#         imap.select()

#         # Zeitraum festlegen (z. B. E-Mails der letzten 'days' Tage)
#         end_date = datetime.date.today()
#         start_date = end_date - datetime.timedelta(days=days)

#         # Suchkriterium mit Zeitraum festlegen
#         search_criteria = f'(SINCE "{start_date.strftime("%d-%b-%Y")}" BEFORE "{end_date.strftime("%d-%b-%Y")}")'
#         status, data = imap.search(None, search_criteria)  # E-Mails im angegebenen Zeitraum abrufen

#         emails = []  # Liste zum Speichern der E-Mails

#         if status == 'OK':
#             email_ids = data[0].split()  # IDs der abgerufenen E-Mails

#             for email_id in email_ids:
#                 status, email_data = imap.fetch(email_id, '(RFC822)')  # E-Mail-Inhalt abrufen
#                 if status == 'OK':
#                     raw_email = email_data[0][1]  # Rohdaten der E-Mail
#                     email_message = email.message_from_bytes(raw_email)  # E-Mail-Objekt erstellen

#                     # Betreff dekodieren
#                     subject = decode_header(email_message['Subject'])
#                     decoded_subject = subject[0][0].decode(subject[0][1]) if subject[0][1] else subject[0][0]

#                     # Anhänge extrahieren
#                     attachments = []
#                     for part in email_message.walk():
#                         if part.get_content_type() == 'application/octet-stream':
#                             attachment = {
#                                 'filename': part.get_filename(),
#                                 'content': part.get_payload(decode=True)
#                             }
#                             attachments.append(attachment)

#                     # Textinhalt der E-Mail extrahieren
#                     text_content = self.extract_text_content(email_message)

#                     # E-Mail-Details in einem Dictionary speichern und zur Liste hinzufügen
#                     email_details = {
#                         'sender': email_message['From'],
#                         'recipients': email_message['To'],
#                         'date': email_message['Date'],
#                         'subject': decoded_subject,
#                         'content': text_content.decode() if isinstance(text_content, bytes) else text_content # Make sure it's a string
#                     }                    
#                     emails.append(email_details)

#         # Verbindung trennen
#         imap.logout()

#         # Rückgabe der abgerufenen E-Mails als Liste von Dictionaries
#         return emails
    
#     def remove_links(self, text):
#         """
#         Entfernt alle URLs aus einem gegebenen Text.

#         Parameters:
#         text (str): Der Text, aus dem die URLs entfernt werden sollen.

#         Returns:
#         str: Der Text ohne URLs.
#         """

#         url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
#         no_url_text = url_pattern.sub('', text)

#         return no_url_text    
    
#     def summarize(self, email_input):
#         """
#         Summarizes an email by returning a string with the date, sender, subject, and first 400 characters of the content.

#         Parameters:
#         email (dict): The email to summarize.

#         Returns:
#         email (dict): A summary of the email.
#         """

#         # Parse the date
#         date = email_input.get('date', '')
        
#         # Remove timezone descriptor such as (CEST)
#         date = date.split('(')[0].strip()

#         # Replace 'GMT' with '+0000' which is the equivalent UTC offset
#         date = date.replace('GMT', '+0000')

#         parsed_date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
#         formatted_date = parsed_date.strftime('%d.%m.%Y %H:%M:%S')

#         # Get the sender and subject
#         sender = email_input.get('sender', '')
#         subject = email_input.get('subject', '')

#         # Get the first 400 characters of the content
#         content = email_input.get('content', '')
#         summarized_content = (content[:400] + '..') if len(content) > 400 else content

#         email = {
#             'date': formatted_date,
#             'sender': sender,
#             'subject': subject,
#             'content': summarized_content,
#         }

#         try:
#             js = json.dumps(email)
#         except Exception as e:
#             return {}

#         return email

    
#     @classmethod
#     def extract_text_content(self, email_message):
#         """
#         Extrahiert den Textinhalt aus einem E-Mail-Objekt.
#         """
#         text_content = ''
#         if email_message.is_multipart():
#             for part in email_message.walk():
#                 text_content += self.extract_content(part)
#         else:
#             text_content = self.extract_content(email_message)

#         return text_content

#     @classmethod
#     def extract_content(self, message_part):
#         """
#         Extrahiert den Inhalt aus einem Teil der E-Mail.
#         """
#         content = ''
#         content_type = message_part.get_content_type()

#         if content_type == 'text/plain':
#             charset = message_part.get_content_charset()
#             email_content = message_part.get_payload(decode=True)

#             if charset:
#                 email_content = email_content.decode(charset)

#             content = email_content

#         elif content_type == 'text/html':
#             charset = message_part.get_content_charset()
#             email_content = message_part.get_payload(decode=True)

#             if charset:
#                 email_content = email_content.decode(charset)

#             # HTML-Inhalt in einfachen Text umwandeln
#             h = html2text.HTML2Text()
#             h.ignore_links = True  # Links ignorieren, nur Text extrahieren
#             content = h.handle(email_content)

#         return content