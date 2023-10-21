from __future__ import print_function

import os.path
import datetime
import logging as log

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# LABEL ID's
# These were queried from service.users().labels().list(userId='me).execute()
# and iterated `label in labels`, printing label['name'] and label['id']

label_30d = 'Label_7629676837455866619'
label_60d = 'Label_6333807318822307091'
label_90d = 'Label_8043081018145399528'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secrets/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        #results = service.users().labels().list(userId='me').execute()

        def trash_messages_before(before, labelIds=None):

            results = service.users().messages().list(userId='me', labelIds=labelIds or [], q=f'before:{before}').execute()
            messages = results.get('messages', [])

            if not messages:
                log.info('NO messages to delet ')
                return

            log.info(f'Trashing {len(messages)} messages')
            for message in messages:
                result = service.users().messages().trash(userId='me', id=message['id']).execute()
                print(result)
                #message_data = service.users().messages().get(userId='me', id=message['id']).execute()


        days_30_ago = (datetime.datetime.now() - datetime.timedelta(30)).strftime('%Y/%m/%d')
        days_60_ago = (datetime.datetime.now() - datetime.timedelta(60)).strftime('%Y/%m/%d')
        days_90_ago = (datetime.datetime.now() - datetime.timedelta(90)).strftime('%Y/%m/%d')

        trash_messages_before(days_30_ago, [label_30d, 'INBOX'])
        trash_messages_before(days_60_ago, [label_60d, 'INBOX'])
        trash_messages_before(days_90_ago, [label_90d, 'INBOX'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        log.error(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
