import click
import torch
from transformers import logging as hf_logging
from train.model import ADClassifier
from train.predict import single_prediction


hf_logging.set_verbosity_error()

@click.command()
@click.option('--sentence', prompt='your sentence', help='This is a string that indicate what you want to classify')
def prediction(sentence):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = ADClassifier(len(['0', '1'])).to(device)
    score, label = single_prediction(model, sentence)
    if label == 0:
        click.echo('This content is NOT an AD article, the probability is {0}'.format(score))
    else:
        click.echo('This content is an AD article, the probability is {0}'.format(score))

if __name__ == '__main__':
    prediction()
