#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
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
import os.path
import smtplib
import datetime
from email import encoders
from email.utils import formatdate
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pya3rt
import gensim

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class GmailReceive(object):
    SCOPES = 'https://mail.google.com/'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Gmail Client'

    def __init__(self, **kwargs):
        if "user_id" in kwargs:
            self.user_id = user_id
        else:
            self.user_id = "me"

        credentials = self.credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = build('gmail', 'v1', http=http)

    # Gmail credential
    def credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python-quickstart.json')
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    # get mail list
    def get_messages(self, q=""):
        try:
            results = self.service.users().messages().list(userId=self.user_id, q=q).execute()
            for msg in results.get("messages", []):
                message = self.service.users().messages().get(userId=self.user_id, id=msg["id"], format='raw').execute()
                msg_str = base64.urlsafe_b64decode(message['raw']).decode("utf-8")
                self.msg = email.message_from_string(msg_str)
                yield self
        except errors.HttpError as error:
            raise ("An error occurred: %s" % error)

    # get subject
    @property
    def subject(self):
        subjects = email.header.decode_header(self.msg.get("Subject"))
        for subject in subjects:
            if isinstance(subject[0], bytes) and subject[1] is not None:
                return subject[0].decode(subject[1], "ignore")
            else:
                return subject[0]

    # get body
    @property
    def body(self):
        if self.msg.is_multipart():
            for payload in self.msg.get_payload():
                if payload.get_content_type() == "text/plain":
                    charset = self.msg.get_param("charset")
                    return payload.get_payload(decode=True).decode('utf-8', 'ignore')
        else:
            charset = self.msg.get_param("charset")
            return self.msg.get_payload(decode=True).decode(charset, 'ignore')


class GmailSend():
    # sender Gmail acount
    ADDRESS = '<SENDER ADDRESS>'
    PASSWARD = '<SENDER PASS>'

    # SMTP setting for GMAIL
    SMTP = "smtp.gmail.com"
    PORT = 587

    def __init__(self,
                 from_addr=None,
                 to_addr=None,
                 subject=None,
                 body=None,
                 mime=None,
                 attach_file=None):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
        self.mime = mime
        self.attach_file = attach_file

    #create message to send
    def create_message(self):
        #message setting
        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr
        msg["Date"] = formatdate()
        msg["Subject"] = self.subject
        body = MIMEText(self.body)
        msg.attach(body)

        # attach file
        if self.mime != None and self.attach_file != None:
            attachment = MIMEBase(self.mime['type'], self.mime['subtype'])
            file = open(self.attach_file['path'])
            attachment.set_payload(file.read())
            file.close()
            Encoders.encode_base64(attachment)
            msg.attach(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=self.attach_file['name'])
        return msg

    #excute send
    def send(self,msg):
        smtpobj = smtplib.SMTP(SMTP,  PORT)
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login(ADDRESS, PASSWARD)
        smtpobj.sendmail(self.from_addr, self.to_addr, msg.as_string())
        smtpobj.close()


class TextCorrection():
    def __init__(self,doc=None):
        self.doc = doc

    def get_sent(self):
        sentences = self.doc.split("。")
        return sentences

    def get_ret(self):
        rets = []
        sentences = self.get_sent()
        for sentence in sentences:
            rets.append(self.sent_correct(sentence))
        return rets

    def sent_correct(self, sentence):
        apikey = "<apikey>"
        client = pya3rt.ProofreadingClient(apikey)
        ret = client.proofreading(sentence)
        status = ret["status"]
        if status == 1:
            checkedSentence = ret["alerts"][0]["checkedSentence"]
            alertDetail = ret["alerts"][0]["alertDetail"]
            checkedWord = ret["alerts"][0]["word"]
            alertCode = ret["alerts"][0]["alertCode"]
            ret_pair = [sentence, status, checkedSentence, alertDetail, checkedWord, alertCode]
        else:
            ret_pair = [sentence, status]
        return ret_pair


class wordSuggest():
    def __init__(self, rets=None, model=None):
        self.rets = rets
        self.model = gensim.models.word2vec.Word2Vec.load(model)

    def word_suggest(self):
        suggestedRets = []
        for ret in self.rets:
            if ret[1] == 1:
                if ret[5] == 0 or ret[5] == 1:
                    suggestedWord = self.wordSuggest(ret[4])
                    ret.append(suggestedWord)
            suggestedRets.append(ret)
    def wordSuggest(self,word):

        suggestedWords = self.model.most_similar(positive=word)
        return suggestedWords

    return suggestedRets

