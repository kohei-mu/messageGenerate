from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from .ml import gec

app = FastAPI()
templates = Jinja2Templates(directory='/opt/templates/')

# TEST
@app.get('/hello')
async def hello():
  return 'Welcome! MyApp!'

# Grammatical Error Correction
@app.get('/gec')
def gec_get(request: Request):
    result = ' '
    return templates.TemplateResponse('gec.html', context={'request': request, 
                                                           'result': result, 
                                                           'color': 'white'})
@app.post('/gec')
def gec_post(request: Request, text: str = Form(...)):
    gec_result = gec(text)
    if gec_result['status'] == 0:
        result = text
        return templates.TemplateResponse('gec.html', context={'request' : request, 
                                                               'result' : result, 
                                                               'text' : text, 
                                                               'color' : '#7cfc00', 
                                                               'comment1' : '正しい文章です。'})
    # when grammatical error detected
    else:
        correction = gec_result['checkedSentence'].replace(' <<',' 【').replace('>> ','】 ')
        text_listed = list(text)
        for corrected in gec_result['alerts']:
            # replace grammatical error word with best suggested word
            text_listed[corrected['pos']] = corrected['suggestions'][0]
        result = "".join(text_listed)
        return templates.TemplateResponse('gec.html', context={'request': request, 
                                                               'result': result, 
                                                               'text' : text, 
                                                               'correction' : correction, 
                                                               'color' : '#ff6347', 
                                                               'comment1' : '校正結果:', 
                                                               'comment2' : '指摘箇所:'})


