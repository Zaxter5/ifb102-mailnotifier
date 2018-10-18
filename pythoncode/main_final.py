from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json
import os.path
import auth
import arrow
import time
from gpiozero import LED
ledPin = LED(17)

import talkey
tts = talkey.Talkey()

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

def GetThread(service, user_id, thread_id):
    """Get a Thread.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        thread_id: The ID of the Thread required.

      Returns:
        Thread with matching ID.
    """
    try:
        thread = service.users().threads().get(userId=user_id, id=thread_id).execute()
        messages = thread['messages']
        return thread
    except:
        print('An error occurred')

def printCurrentDateTime():
    dateTime = arrow.now()
    return str(dateTime.day) + "/" + str(dateTime.month) + "/" + str(dateTime.year) + " - " + str(dateTime.hour) + ":" + str(dateTime.minute) + ":" + str(dateTime.second) 

def speakMessage(m):
	tts.say(m)

def init():
    while True:
        editOrRun = raw_input("Would you like to [E]dit or [R]un?")
        if editOrRun == "E":
            timeOrEmail = raw_input("Would you like to change the check interval [T]ime or change your [E]mail? Or [C]ancel.")
            if timeOrEmail == "T":
                time_input = raw_input("Please type your desired time in SECONDS:")
                time_input = {u"check_interval":[time_input]}
                with open('check_interval.json', 'w') as outfile:
                    json.dump(time_input, outfile)
                outfile.close()
                continue
            elif timeOrEmail == "E":
                email_input = raw_input("Please type your Gmail address - this is case sensitive:")
                print(email_input)
                email_array = {u"email_array":[email_input]}
                with open('email.json','w') as outfile:
                    json.dump(email_array, outfile)
                outfile.close()
                continue
            elif timeOrEmail == "C":
                continue
            else:
                print("Please type a valid input - T, E or C.")
                continue
        elif editOrRun == "R":
            if (not os.path.isfile("./email.json")) or (not os.path.isfile("./check_interval.json")):
                print("No email or check interval has been set!")
                print("Please set these in the [E]dit menu.")
                continue
            else:
                loop = True
                break
        else:
            print("Please type a valid input - E or R.")
            continue



################AUTHORISATION################
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'IFB102 Email Notifier'
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.get_credentials()
service = build('gmail', 'v1', http=credentials.authorize(Http()))
init()

with open('email.json') as infile:
    email_array = json.load(infile)
    user_id = email_array["email_array"][0]
infile.close()

with open('check_interval.json') as infile:
    delay_time = json.load(infile)
    delay_time = int(delay_time["check_interval"][0])
infile.close()
############################################

while True:
    messages = ListMessagesMatchingQuery(service, user_id, query='')
    current_messages = int(len(messages))
    unread_count = 0

    for i in range(current_messages):
        thread = GetThread(service, user_id, messages[i]["threadId"])
        if 'UNREAD' in thread["messages"][0]["labelIds"]:
            unread_count = unread_count + 1

    if os.path.isfile('./message_count.json'):
        with open('message_count.json') as infile:
            message_count = json.load(infile)
            old_messages = message_count["old_messages"]
            old_messages = old_messages[0]
            if unread_count > old_messages:
                ledPin.on()
                print(printCurrentDateTime())
                            
                print("You have " + str(unread_count - old_messages) + " new messages since last check!")
                print("You have " + str(unread_count) + " unread messages!")
                speakMessage("You have " + str(unread_count - old_messages) + " new messages since last check!")
                speakMessage("You have " + str(unread_count) + " unread messages!")

                message_count = {u"old_messages":[unread_count]}
                with open('message_count.json', 'w') as outfile:
                    json.dump(message_count, outfile)
                outfile.close()

            elif unread_count == 0:
                ledPin.off()

                print(printCurrentDateTime())
                print("You have no new or unread messages!")
                speakMessage("You have no new or unread messages!")
                
            elif unread_count <= old_messages:
                ledPin.on()

                message_count = {u"old_messages":[unread_count]}
                with open('message_count.json', 'w') as outfile:
                    json.dump(message_count, outfile)
                outfile.close()

                print(printCurrentDateTime())
                print("You have " + str(unread_count) + " unread messages!")
                speakMessage("You have " + str(unread_count) + " unread messages!")


        infile.close()
    else:
        message_count = {u"old_messages":[unread_count]}
        with open('message_count.json', 'w') as outfile:
            json.dump(message_count, outfile)
        outfile.close()
    time.sleep(delay_time)      