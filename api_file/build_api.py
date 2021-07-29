import torch
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import logging as hf_logging
from typing import Dict


from train.model import ADClassifier
from train.predict import single_prediction

hf_logging.set_verbosity_error()
logging.basicConfig()

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = ADClassifier(len(['0', '1'])).to(device)

app = FastAPI(title="AD classifier API", description="A simple API using fine-tuning albert to predict the AD content")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# templates = Jinja2Templates(directory="templates")
@app.get('/')
def index():
    return {'message': 'This is the homepage of the API '}


@app.post("/predict")
def predict_content( content: str):
    """
    A simple function that receive a text content and predict if it is AD article.
    input param: content
    return: prediction, probabilities
    """
    score, label = single_prediction(model, content)
    prediction = {0:'negative', 1:'positive'}
    result = {'prediction': prediction[label], 'probability': score}
    return result

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', debug=True)





