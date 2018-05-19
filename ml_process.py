# -*- coding: utf-8 -*-
import re
import urllib.request
import json

class TextCorrection():
    def apifunc(self, sentence):
        API_URL = "https://api.a3rt.recruit-tech.co.jp/proofreading/v2/typo"
        post_data = {
            "apikey": "<API_KEY>",
            "sentence": sentence,
        }
        encoded_post_data = urllib.parse.urlencode(post_data).encode(encoding='utf-8')
        page_text = ""
        with urllib.request.urlopen(url=API_URL, data=encoded_post_data) as page:
            for line in page.readlines():
                page_text = page_text + line.decode('utf-8')
        data = json.loads(page_text)
        return data

    def getCorrection(self, doc):
        retlines = []
        lines = list(filter(lambda w: len(w) > 0, re.split(r"。|？|\?|\!|！|～|", doc)))
        for line in lines:
            data = self.apifunc(line)
            status = data['status']
            input = data['inputSentence']
            if status == 1:
                checked = data['checkedSentence']
                alert = data['alerts']
                corList = []
                for j in range(0, len(alert)):
                    correctionSuggest = alert[j]['suggestions']
                    word = alert[j]['word']
                    correctpairs = str(word) + ":" + str(correctionSuggest)
                    corList.append(correctpairs)
                retline = [input, checked, corList]
            else:
                retline = [input]
            retlines.append(retline)
        return retlines




