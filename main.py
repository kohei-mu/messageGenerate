from mail_process import MailList
import sys

#mail check
mailCheck = MailList()
#list of mail ids
mailList = mailCheck.getMailList()
#if unread mali list is None, exit the program
if len(mailList) == 0:
    sys.exit()
else:
    #import libraries
    from mail_process import UpdateMailStatus,MailSend
    from ml_process import TextCorrection,WordSuggestion

#get mail ids if unread mails exist
if mailList != []:
    ids = [i["id"] for i in mailList]

#get messages by ids
mails = mailCheck.getMessage(msg_ids=ids)

#correct document and suggest words
textCorrect = TextCorrection()
wordSuggest = WordSuggestion(model="entity_vector.model.bin")
corrected_dic = {}
for mail in mails:
    subject = mail[0]
    body = mail[1]
    #print(body)
    correctedBody = textCorrect.getCorrection(doc=body)
    suggested = wordSuggest.getSuggestion(rets=correctedBody)
    corrected_dic[subject] = suggested

#shape mail body into easy to read  style
shapedCorrected_dic = {}
for subject,bodies in corrected_dic.items():
    shapedList = []
    for body in bodies:
        if body[1] == 0: #if no need to correct words
            bodyShaped = "本文 (訂正無) : " + body[0] + "\n"
        else:
            _body = "本文 (訂正有) : " + body[0] + "\n"
            correctedBody = "訂正文 : " + body[2] + "\n"
            comment = "訂正レベル : " + body[3] + "\n"
            suggested = "推薦 (推薦語,類似度) : " + str(body[6]) + "\n"
            bodyShaped = [_body,correctedBody, comment, suggested]
        shapedList.append(bodyShaped)
    shapedCorrected_dic["Re:" + subject] = shapedList

#send mails
sendMail = MailSend()
for subject, bodies in shapedCorrected_dic.items():
    bodiesToSend = ["".join(body) + "\n" for body in bodies]
    msg = sendMail.createMessage(subject=subject,body="".join(bodiesToSend),mime=None,attach_file=None)
    sendMail.sendMessage(msg=msg)

#remove "unread" staus from gmail so as not to include next batch excution
statusUpdate = UpdateMailStatus()
#update status by ids
for id in ids:
    statusUpdate.updateStatus(msg_id=id)

