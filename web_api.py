import os
import torch

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from starlette.responses import RedirectResponse
from transformers import logging as hf_logging

from train.model import ADClassifier
from train.predict import single_prediction



hf_logging.set_verbosity_error()

os.environ['CUDA_VISIBLE_DEVICES'] = ""
os.environ['BEST_MODEL'] = "./model/run/best_model_state_22.bin"

class Settings(BaseSettings):
    device: str = 'cpu'
    n_classes: int = 2
    best_model: str
    max_len: int =300


settings = Settings()
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = ADClassifier(settings.n_classes).to(torch.device(settings.device))

app = FastAPI(title="AD classifier API", description="A simple API using fine-tuning albert to predict the AD content")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def redirect():
    response = RedirectResponse(url='/predict')
    return response

@app.get("/predict")
async def index(request: Request):
    results = "No result yet..."
    return templates.TemplateResponse('index.html', context={'request': request, 'results': results})

@app.post("/predict")
async def from_post(request: Request, content: str = Form(...)) :
    score = []
    label = []
    prediction = {0:'negative', 1:'positive'}

    number = 'You input {} text contents, the results of them: '.format(len(content.splitlines()))

    for sentence in content.splitlines():
        score.append(single_prediction(model, sentence,
                                       settings.best_model,
                                       settings.max_len,
                                       torch.device(settings.device))[0])

        label.append(prediction[single_prediction(model, sentence,
                                                  settings.best_model,
                                                  settings.max_len,
                                                  torch.device(settings.device))[1]])

    results = [{'id':idx+1, 'result':item} for idx, item in enumerate([[i,j] for i,j in zip(label,score)])]
    return templates.TemplateResponse('index.html', context={'request': request, 'results': results, 'number': number})


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', debug=True)
