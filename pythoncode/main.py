from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import os.path
import auth
from apiclient import errors

def ListMessagesMatchingQuery(service, user_id, query=''):
  #List all Messages of the user's mailbox matching the query.

 # Args:
   # service: Authorized Gmail API service instance.
   # user_id: User's email address. The special value "me"
   # can be used to indicate the authenticated user.
   # query: String used to filter messages returned.
   # Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

 # Returns:
  #  List of Messages that match the criteria of the query. Note that the
  #  returned list contains Message IDs, you must use get with the
  #  appropriate ID to get the details of a Message.

    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if response.__contains__('messages'):
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except:
        print('An error occurred')

################AUTHORISATION################
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'IFB102 Email Notifier'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.get_credentials()
service = build('gmail', 'v1', http=credentials.authorize(Http()))
user_id = 'zach.ifb102@gmail.com'
############################################


messages = ListMessagesMatchingQuery(service, user_id, query='')
current_messages = int(len(messages))

if os.path.isfile('./message_count.json'):
    with open('message_count.json') as infile:
        message_count = json.load(infile)
        old_messages = message_count["old_messages"]
        old_messages = old_messages[0]
        if current_messages > old_messages:
            print("You have " + str(current_messages - old_messages) + " new messages!")
            message_count = {u"old_messages":[current_messages]}
            with open('message_count.json', 'w') as outfile:
                json.dump(message_count, outfile)
            outfile.close()
        else:
            print("You have no new mail!")
    infile.close()
else:
    message_count = {u"old_messages":[current_messages]}
    with open('message_count.json', 'w') as outfile:
        json.dump(message_count, outfile)
    outfile.close()      
