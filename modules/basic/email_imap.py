import pickle
import os
from core import cfg, log, DEBUG_LEVEL_MAX
from linguflex_functions import linguflex_function
from email_imap_helper import EmailFetcher
from datetime import datetime, timedelta

fetcher = EmailFetcher(cfg('server'), cfg('username'), cfg('password'))
history_days = int(cfg('history_days'))

CHECK_TIME_FILE='email_last_check_time.pkl'

@linguflex_function
def retrieve_emails(mailbox='INBOX'):
    "Returns current emails; mailbox: name of the mailbox to retrieve emails from; default is 'INBOX'"
    log(DEBUG_LEVEL_MAX, "  [retrieve_emails] Start fetching emails...")

    imap = fetcher.connect_to_server()
    email_ids = fetcher.search_emails(imap, history_days, mailbox)
    emails = fetcher.fetch_emails(imap, email_ids)
    emails.reverse()
    log(DEBUG_LEVEL_MAX, f"  [retrieve_emails] Fetched {len(emails)} emails successfully")

    # Close the connection to the IMAP server
    imap.logout()

    # Limit the number of emails to 10
    emails = emails[:10]

    last_check_time = get_last_check_time()

    # filter out emails that are older than last_check_time
    emails = [email for email in emails if datetime.strptime(email['date'], '%d.%m.%Y %H:%M:%S') > last_check_time]

    store_last_check_time(datetime.today())    

    # last_check_time = get_last_check_time()

    # # filter out emails that are older than last_check_time
    # # the current date is in 'date' like that: 
    # # for email in emails:
    # #   mail_date = email['date'] # formatted as in datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z').strftime('%d.%m.%Y %H:%M:%S')

    # emails = [email for email in emails if datetime.strptime(email['date'], '%a, %d %b %Y %H:%M:%S %z') > last_check_time]

    # store_last_check_time(datetime.today())

    return {"last check time": str(last_check_time), "emails": emails}
    #return emails


def store_last_check_time(check_time):
    """
    Stores the time of the last email check to a file.

    :param check_time: The time of the last email check.
    """
    with open(CHECK_TIME_FILE, 'wb') as f:
        pickle.dump(check_time, f)

def get_last_check_time():
    """
    Retrieves the time of the last email check from a file. If the file doesn't exist, return the current time minus 7 days.

    :return: The time of the last email check.
    """
    if not os.path.exists(CHECK_TIME_FILE):
        return datetime.today() - timedelta(days=7)
    with open(CHECK_TIME_FILE, 'rb') as f:
        return pickle.load(f)   
