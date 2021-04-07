#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from oauth2client import file
import os.path
import smtplib
from email.utils import formatdate
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httplib2
import os
import base64
import email
from apiclient import *
from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret2.json'
APPLICATION_NAME = 'Gmail Client'

### general functions ###
def credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'gmail-python-quickstart2.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

service = build('gmail', 'v1', http=credentials().authorize(httplib2.Http()))

#check unread mail and get subject and body of it
class MailList():
    def __init__(self, user_id="me",query='newer_than:1H is:unread'):
        self.user_id = user_id
        self.query = query

    #check unread  mail
    def getMailList(self):
      try:
        response = service.users().messages().list(userId=self.user_id, q=self.query).execute()
        messages = []
        if 'messages' in response:
          messages.extend(response['messages'])

        while 'nextPageToken' in response:
          page_token = response['nextPageToken']
          response = service.users().messages().list(userId=self.user_id, q=self.query,pageToken=page_token).execute()
          messages.extend(response['messages'])
        return messages
      except errors.HttpError as error:
        print('An error occurred: %s' % error)

    #get subject and body
    def getMessage(self, msg_ids):
      if msg_ids == []:
          print("messages not found")
          return None
      try:
        mails = []
        for msg_id in msg_ids:
            message = service.users().messages().get(userId=self.user_id, id=msg_id, format='raw').execute()
            email_str = base64.urlsafe_b64decode(message['raw']).decode("utf-8")
            msg = email.message_from_string(email_str)
            #subject
            subject = email.header.decode_header(msg.get("Subject"))[0][0]
            #body
            _body = [payload.get_payload(decode=True).decode('utf-8', 'ignore') for payload in msg.get_payload()][0]
            body = _body.replace("\r\n", "")
            mails.append((subject,body))
        return mails
      except errors.HttpError as error:
        print('An error occurred: %s' % error)

# email sending class
class MailSend():
    def __init__(self):
        self.from_addr = '<sender address>'
        self.to_addr = '<receiver address>'

    #create message and return it
    def createMessage(self, subject, body, mime, attach_file):
        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr
        msg["Date"] = formatdate()
        msg["Subject"] = subject
        body = MIMEText(body)
        msg.attach(body)

        #for attach file
        if mime != None and attach_file != None:
            attachment = MIMEBase(mime['type'], mime['subtype'])
            file = open(attach_file['path'])
            attachment.set_payload(file.read())
            file.close()
            Encoders.encode_base64(attachment)
            msg.attach(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=attach_file['name'])
        return msg

    #send created message
    def sendMessage(self,msg):
        smtpobj = smtplib.SMTP("smtp.gmail.com",  587)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login('<mail address>', '<password>')
        smtpobj.sendmail(self.from_addr, self.to_addr, msg.as_string())
        smtpobj.close()

class UpdateMailStatus():
    def __init__(self, user_id="me", msg_labels={'removeLabelIds': ['UNREAD'], 'addLabelIds': []}):
        self.user_id = user_id
        self.msg_labels = msg_labels

    #update mail status (unread to read)
    def updateStatus(self,msg_id):
      try:
        message = service.users().messages().modify(userId=self.user_id, id=msg_id,body=self.msg_labels).execute()
        return message
      except errors.HttpError as error:
        print('An error occurred: %s' % error)

