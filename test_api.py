import click
import requests


@click.command()
@click.option('--content', prompt='please type your content', help='This is a string that indicate what you want to classify')
def response_text(content):
    url = "http://127.0.0.1:8000/predict?content="
    headers = {'accept':'application/json'}
    response = requests.request("POST", url, headers=headers, data=content.encode('utf-8'))
    click.echo(response.text)

if __name__ == '__main__':
    response_text()
