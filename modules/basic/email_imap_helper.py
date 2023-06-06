import imaplib
import email
import datetime
from email.header import decode_header
import html2text
import re

class EmailFetcher:
    """
    Diese Klasse dient zum Abrufen von E-Mails von einem IMAP-Server.
    """

    def __init__(self, imap_server, username, password):
        """
        Initialisiert die Klasse mit den notwendigen Server-, Benutzer- und Passwortinformationen.
        """
        self.imap_server = imap_server
        self.username = username
        self.password = password

    def get_mails(self, days):
        """
        Abrufen von E-Mails von 'days' Tagen in die Vergangenheit.
        """
        # Verbindung zum IMAP-Server herstellen
        imap = imaplib.IMAP4_SSL(self.imap_server)
        imap.login(self.username, self.password)

        # Postfach auswählen (Standard-Ordner "INBOX")
        imap.select()

        # Zeitraum festlegen (z. B. E-Mails der letzten 'days' Tage)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=days)

        # Suchkriterium mit Zeitraum festlegen
        search_criteria = f'(SINCE "{start_date.strftime("%d-%b-%Y")}" BEFORE "{end_date.strftime("%d-%b-%Y")}")'
        status, data = imap.search(None, search_criteria)  # E-Mails im angegebenen Zeitraum abrufen

        emails = []  # Liste zum Speichern der E-Mails

        if status == 'OK':
            email_ids = data[0].split()  # IDs der abgerufenen E-Mails

            for email_id in email_ids:
                status, email_data = imap.fetch(email_id, '(RFC822)')  # E-Mail-Inhalt abrufen
                if status == 'OK':
                    raw_email = email_data[0][1]  # Rohdaten der E-Mail
                    email_message = email.message_from_bytes(raw_email)  # E-Mail-Objekt erstellen

                    # Betreff dekodieren
                    subject = decode_header(email_message['Subject'])
                    decoded_subject = subject[0][0].decode(subject[0][1]) if subject[0][1] else subject[0][0]

                    # Anhänge extrahieren
                    attachments = []
                    for part in email_message.walk():
                        if part.get_content_type() == 'application/octet-stream':
                            attachment = {
                                'filename': part.get_filename(),
                                'content': part.get_payload(decode=True)
                            }
                            attachments.append(attachment)

                    # Textinhalt der E-Mail extrahieren
                    text_content = self.extract_text_content(email_message)

                    # E-Mail-Details in einem Dictionary speichern und zur Liste hinzufügen
                    email_details = {
                        'sender': email_message['From'],
                        'recipients': email_message['To'],
                        'date': email_message['Date'],
                        'subject': decoded_subject,
                        'content': text_content,
                        'attachments': attachments
                    }
                    emails.append(email_details)

        # Verbindung trennen
        imap.logout()

        # Rückgabe der abgerufenen E-Mails als Liste von Dictionaries
        return emails
    
    def remove_links(self, text):
        """
        Entfernt alle URLs aus einem gegebenen Text.

        Parameters:
        text (str): Der Text, aus dem die URLs entfernt werden sollen.

        Returns:
        str: Der Text ohne URLs.
        """

        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        no_url_text = url_pattern.sub('', text)

        return no_url_text    
    
    def summarize(self, email):
        """
        Summarizes an email by returning a string with the date, sender, subject, and first 400 characters of the content.

        Parameters:
        email (dict): The email to summarize.

        Returns:
        str: A summary of the email.
        """

        # Parse the date
        date = email.get('date', '')
        
        # Remove timezone descriptor such as (CEST)
        date = date.split('(')[0].strip()

        # Replace 'GMT' with '+0000' which is the equivalent UTC offset
        date = date.replace('GMT', '+0000')

        parsed_date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
        formatted_date = parsed_date.strftime('%d.%m.%Y %H:%M:%S')

        # Get the sender and subject
        sender = email.get('sender', '')
        subject = email.get('subject', '')

        # Get the first 400 characters of the content
        content = email.get('content', '')
        summarized_content = (content[:400] + '..') if len(content) > 400 else content

        # Construct the summary
        summary = f"Date and Time: {formatted_date}, Sender: {sender}, Subject: {subject}, Content: {summarized_content}"

        return summary

    
    @classmethod
    def extract_text_content(self, email_message):
        """
        Extrahiert den Textinhalt aus einem E-Mail-Objekt.
        """
        text_content = ''
        if email_message.is_multipart():
            for part in email_message.walk():
                text_content += self.extract_content(part)
        else:
            text_content = self.extract_content(email_message)

        return text_content

    @classmethod
    def extract_content(self, message_part):
        """
        Extrahiert den Inhalt aus einem Teil der E-Mail.
        """
        content = ''
        content_type = message_part.get_content_type()

        if content_type == 'text/plain':
            charset = message_part.get_content_charset()
            email_content = message_part.get_payload(decode=True)

            if charset:
                email_content = email_content.decode(charset)

            content = email_content

        elif content_type == 'text/html':
            charset = message_part.get_content_charset()
            email_content = message_part.get_payload(decode=True)

            if charset:
                email_content = email_content.decode(charset)

            # HTML-Inhalt in einfachen Text umwandeln
            h = html2text.HTML2Text()
            h.ignore_links = True  # Links ignorieren, nur Text extrahieren
            content = h.handle(email_content)

        return content