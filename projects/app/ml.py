import requests
import json
import os

API_KEY = os.getenv("A3RT_KEY")

def gec(text):
    _url = "https://api.a3rt.recruit-tech.co.jp/proofreading/v2/typo?apikey={KEY}&sentence={TEXT}"
    url = _url.format(KEY=API_KEY, TEXT=text)
    response = requests.get(url)
    data = response.json()
    return data

