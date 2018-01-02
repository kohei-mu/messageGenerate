# -*- coding: utf-8 -*-
import gensim
import pya3rt
import re

#word correcttion claa
class TextCorrection():
    #get sentence/corrected sentence return
    def getCorrection(self, doc):
        rets = []
        sentences = list(filter(lambda w:len(w) >0, re.split(r"。|？|\?|\!|！|～|、|", doc)))
        for sentence in sentences:
            # call correction function
            rets.append(self.correctSentence(sentence))
        return rets

    #call word correction function
    def correctSentence(self, sentence):
        apikey = "<API key>"
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

#word suggest class
class WordSuggestion():
    def __init__(self, model=None):
        #for light model
        #self.model = gensim.models.word2vec.Word2Vec.load(model)
        self.model = gensim.models.KeyedVectors.load_word2vec_format(model, binary=True)

    #call word suggestion function and get returns  and make a list of them
    def getSuggestion(self, rets):
        suggestedRets = []
        for ret in rets:
            if ret[1] == 1:
                if ret[5] == 0 or ret[5] == 1 or ret[5] == 2:
                    suggestedWord = self.model.most_similar(positive=ret[4])
                    ret.append(suggestedWord)
            suggestedRets.append(ret)
        return suggestedRets


