import argparse
import base64
import os
import subprocess
from tempfile import NamedTemporaryFile
from typing import List

import numpy as np
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.templating import Jinja2Templates

# import settings

app = FastAPI()
templates = Jinja2Templates(directory='api/templates')
model_selection_options = ['bert-based', 'lstm-crf']
model_dict = {'bert-based': '../model/yolov5.pt',
              'lstm-crf': '../model/pedestrian.yml'}  # set up model cache


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse('home.html', {
        "request": request,
        "model_selection_options": model_selection_options,
    })
    
    
def format_result(string):
    split_string = string.split(') (')[1: -1]
    format_string = ' '.join(list(map(lambda x: x.replace(', ', '_').replace("'", ''), split_string)))
    # return list(map(lambda x: list(map(lambda y: str(y).replace("'", ''), x.split(', '))), split_string))
    return format_string


@app.post("/")
async def detect_via_web_form(request: Request,
                              textupload: str = Form(...),
                              model_name: str = Form(...),
                              ):

    # f = open("data/first_text.txt", "w", encoding='utf-8')
    # # print(type(textupload))
    # f.write(textupload.encode('utf-8').decode())
    # f.close()
    
    # rc = subprocess.call(
    #     ["/home/hoang/Desktop/NLP-Ner/api/call_helper.sh", textupload], shell=True)
    # print("Text up load: ", textupload)

    os.system(f'bash /home/hoang/Desktop/NLP_CovidNer/api/call_helper.sh \"{textupload}\"')
    first_text = open("data/first_text.txt", "r", encoding='utf-8')
    # first_text = textupload
    final_result = open("data/final_result.txt", "r")
    result = [{"first_text": first_text.read(), 
               "result": final_result.readlines()}]
    
    for i in range(len(result[0]['result'])):
        result[0]['result'][i] = format_result(result[0]['result'][i])
    final_result.close()
    if model_name == 'bert-based':
        return templates.TemplateResponse('show_results.html', {
            'request': request,
            'json_results': result,
        })

    elif model_name == 'lstm-crf':
        return templates.TemplateResponse('show_results.html', {
            'request': request,
            'json_results': result,
        })

if __name__ == '__main__':
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=8000)
    opt = parser.parse_args()
    app_str = 'server:app'
    uvicorn.run(app_str, host=opt.host, port=opt.port, reload=True)
