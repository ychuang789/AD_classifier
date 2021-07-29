import torch
import logging

import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from transformers import logging as hf_logging

from train.model import ADClassifier
from train.predict import single_prediction



hf_logging.set_verbosity_error()
logging.basicConfig()

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = ADClassifier(len(['0', '1'])).to(device)

app = FastAPI(title="AD classifier API", description="A simple API using fine-tuning albert to predict the AD content")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/")
async def redirect():
    response = RedirectResponse(url='/predict')
    return response

@app.get("/predict")
async def index(request: Request):
    result = "No result yet..."
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})

@app.post("/predict")
async def from_post(request: Request, content: str = Form(...), number: int = Form(...)) :

    if len(content.splitlines()) != number:
        result = "The number of articles does not match the input value, please retry again..."
        return templates.TemplateResponse('index.html', context={'request': request, 'result': result})
    else:
        score = []
        label = []
        prediction = {0:'negative', 1:'positive'}


        for sentence in content.splitlines():
            score.append(single_prediction(model, sentence)[0])
            label.append(prediction[single_prediction(model, sentence)[1]])

        results = [{'id':idx+1, 'result':item} for idx, item in enumerate([[i,j] for i,j in zip(label,score)])]
        return templates.TemplateResponse('index.html', context={'request': request,
                                                                'results': results})


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', debug=True)
