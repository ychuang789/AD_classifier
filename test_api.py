import re
import click
import requests


@click.command()
@click.option('--content', prompt='please type your content', help='This is a string that indicate what you want to classify')
def response_text(content):
    click.echo("calculating the result... please wait for seconds")

    url = "http://127.0.0.1:8000/predict?content="
    headers = {'accept':'application/json'}
    response = requests.request("POST", url, headers=headers, data=content.encode('utf-8'))

    if "negative" in response.text:
        # click.echo(response.text)
        click.echo('This is "NOT" an AD content')
        click.echo('The probability is {}'.format(re.findall(r"\d+\.\d+", response.text)[0]))
    else:
        click.echo('This is an AD content')
        click.echo('The probability is {}'.format(re.findall(r"\d+\.\d+", response.text)[0]))

if __name__ == '__main__':
    response_text()
