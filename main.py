from mail_process import MailList
import sys
import logging
from datetime import datetime


########################  LOGGING SETTING #################################
now = datetime.now().strftime("%Y%m%d")

#set logging output name
logger = logging.getLogger('Logging')

#set log level
logger.setLevel(10)

#set log output file name (datetime + .log)
fh = logging.FileHandler('./'+now+'.log')
logger.addHandler(fh)

#log output to console
sh = logging.StreamHandler()
logger.addHandler(sh)

#set log output format
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
############################################################################

logger.info("#################################### program start ################################################")

#mail check
mailCheck = MailList()
#list of mail ids
mailList = mailCheck.getMailList()
#if unread mali list is None, exit the program
if len(mailList) == 0:
    logger.info("mail is not delivered, so quit the program")
    logger.info("######################################## program end ############################################")
    sys.exit()
else:
    logger.info("mail is delivered, continue the program")
    #import libraries
    from mail_process import UpdateMailStatus,MailSend
    from ml_process import TextCorrection,WordSuggestion

#get mail ids if unread mails exist
if mailList != []:
    ids = [i["id"] for i in mailList]
    logger.info("got the mail ids")

#get messages by ids
try:
    mails = mailCheck.getMessage(msg_ids=ids)
    logger.info("got the mail(subject/body) by the mail id")
except:
    logger.warning("some problem occured in mail getting process")

#correct document and suggest words
textCorrect = TextCorrection()
wordSuggest = WordSuggestion(model="entity_vector.model.bin")
corrected_dic = {}
logger.info("ML process start")
for mail in mails:
    subject = mail[0]
    body = mail[1]
    #print(body)
    try:
        correctedBody = textCorrect.getCorrection(doc=body)
        logger.info("text correction process excuted")
    except:
        logger.warning("some problem occured in text correction process")

    try:
        suggested = wordSuggest.getSuggestion(rets=correctedBody)
        logger.info("word suggestion process excuted")
    except:
        logger.warning("some problem occured in word suggestion process")

    corrected_dic[subject] = suggested
logger.info("ML process end")


logger.info("mail shaping process start")
#shape mail body into easy to read  style
try:
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
    logger.info("mail shaping process end")
except:
    logger.warning("some problem occured in mail shaping process")


logger.info("mail send process start")
try:
    #send mails
    sendMail = MailSend()
    for subject, bodies in shapedCorrected_dic.items():
        bodiesToSend = ["".join(body) + "\n" for body in bodies]
        msg = sendMail.createMessage(subject=subject,body="".join(bodiesToSend),mime=None,attach_file=None)
        sendMail.sendMessage(msg=msg)
except:
    logger.warning("some problem occured in mail send process")
logger.info("mail send process end")


#remove "unread" staus from gmail so as not to include next batch excution
statusUpdate = UpdateMailStatus()
#update status by ids
for id in ids:
    statusUpdate.updateStatus(msg_id=id)
logger.info("mail status updated from unread to read")

logger.info("################################# program successfully excuted ######################################")

