import os
import click
import torch
import pandas as pd
from transformers import logging as hf_logging
from train.model import ADClassifier
from train.predict import single_prediction


hf_logging.set_verbosity_error()

@click.group(help='CLI classifier application file: For multiple content txt file; single: For a single text input.')
def cli():
    pass

@click.command()
@click.argument('device', default= torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
@click.argument('best_model', default= './model/run/best_model_state_22.bin')
@click.argument('max_len', default=300)
@click.option('--sentence', prompt='please type your content here', help='This is a string that indicate what you want to classify')
def single(sentence, device, best_model, max_len):
    click.echo('calculating scores...please wait')

    model = ADClassifier(2).to(device)

    try:
        score, label = single_prediction(model, sentence, best_model, max_len, device)
        click.echo('The prediction is done...printing the results')
        if label == 0:
            click.echo('This content is "NOT" an AD article, the probability is {0}'.format(score))
        else:
            click.echo('This content is an AD article, the probability is {0}'.format(score))
    except:
        click.echo('There is something wrong while getting the prediction...')

@click.command()
@click.argument('device', default= torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
@click.argument('best_model', default= './model/run/best_model_state_22.bin')
@click.argument('max_len', default=300)
@click.option('--path', required=True, prompt='please type your filepath here (support txt file with string format)')
# @click.option('--output_name', type= str,required=True, prompt='please name the output file...')
def file(path, device, best_model, max_len):
    model = ADClassifier(2).to(device)
    try:
        if os.path.isfile(path):
            click.echo('opening file...')
            click.echo('calculating scores...please wait')
            with open(path, 'r') as f:
                lines = f.read().splitlines()

        score = []
        label = []
        prediction = {0:'negative', 1:'positive'}
        for sentence in lines:
            score.append(single_prediction(model, sentence, best_model, max_len, device)[0])
            label.append(prediction[single_prediction(model, sentence, best_model, max_len, device)[1]])

        df = pd.DataFrame(list(zip(lines, label, score)), columns= ['content', 'label', 'probability'])
        output_name = click.prompt('Please enter the output filename', type=str)
        df.to_csv('./model/cli_output/{}.csv'.format(output_name), index= False, encoding= 'utf-8-sig')
        click.echo('Job done!')
    except:
        click.echo('No such file or wrong format (support txt file with string format) please re-check the file!!')



cli.add_command(single)
cli.add_command(file)

if __name__ == "__main__":
    cli()
