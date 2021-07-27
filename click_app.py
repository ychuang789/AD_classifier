import click
import torch
from transformers import logging as hf_logging
from train.model import ADClassifier
from train.predict import single_prediction


hf_logging.set_verbosity_error()


@click.command()
@click.option('--sentence', prompt='please type your content', help='This is a string that indicate what you want to classify')
def prediction(sentence):
    click.echo('calculating scores...please wait')
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = ADClassifier(len(['0', '1'])).to(device)

    try:
        score, label = single_prediction(model, sentence)
        click.echo('The prediction is done...printing the results')
        if label == 0:
            click.echo('This content is "NOT" an AD article, the probability is {0}'.format(score))
        else:
            click.echo('This content is an AD article, the probability is {0}'.format(score))
    except:
        click.echo('There is something run while getting the prediction...')

if __name__ == '__main__':
    prediction()
