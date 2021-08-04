import argparse
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('--path', default='./scrap_file/text.xlsx')
args = parser.parse_args()

def get_text(args):
    df = pd.read_excel(args.path, header= 0)
    df['text'] = df['title'] + df['content']

    with open('test_100.txt', 'w') as f:
        for i in df['text'].astype(str):
            f.write(i+'\n')
        f.close()

if __name__ == '__main__':
    get_text(args)
