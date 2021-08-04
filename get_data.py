import argparse
import logging
import os
import pymysql.cursors
import pandas as pd
from time import time
from tqdm import tqdm


def find_keyword(data):
    with open('keyword.txt', 'r') as f:
        keyword = [line for line in f.read().splitlines()]

    train_title, train_content = filter_test_data('data.pkl')

    save = []
    for item in tqdm(data):
        if list(item.values())[0] not in list(train_title):
            for word in keyword:
                if word not in list(item.values())[0] + ' ' + list(item.values())[1]:
                    save.append(item)
                    continue
        else:
            continue

    return save

def find_without_keyword(data):
    with open('keyword.txt', 'r') as f:
        keyword = [line for line in f.read().splitlines()]

    train_title, train_content = filter_test_data('data.pkl')

    save_wk = []
    for item in tqdm(data):
        if list(item.values())[0] not in list(train_title):
            if any([x in (list(item.values())[0] + list(item.values())[1]) for x in keyword]):
                continue
            else:
                save_wk.append(item)

    return save_wk

def filter_test_data(path):
    train_data = pd.read_pickle(path)
    return train_data['title'], train_data['content']

def to_dataframe(data):
    return pd.DataFrame.from_dict(data)


FUNCTION_MAP = {'positive': find_keyword, 'negative': find_without_keyword}

parser = argparse.ArgumentParser()
parser.add_argument('number', type= int, help= 'total query number from database')
parser.add_argument('command', choices=FUNCTION_MAP.keys(), help= 'select one command, positive or negative')
parser.add_argument('--host', default= os.getenv('HOST'), help= 'host address')
parser.add_argument('--user', default= os.getenv('DB_USER_ID'), help= 'user id')
parser.add_argument('--password', default= os.getenv('DB_USER_PWD'), help= 'user password')

args = parser.parse_args()

def connect_database(db, args):
    try:
        config = {
            'host': args.host,
            'user': args.user,
            'password': args.password,
            'db':db,
            'charset':'utf8mb4',
            'cursorclass':pymysql.cursors.DictCursor,
        }
        connection = pymysql.connect(**config)
        return connection

    except:
        logging.error('Fail to connect to database.')



if __name__ == "__main__":
    start_time = time()
    func = connect_database
    relative_func = FUNCTION_MAP[args.command]
    number = args.number
    with func('forum_data', args).cursor() as cursor:
        sql = "SELECT title, content FROM ts_page_content LIMIT {0}".format(number)
        cursor.execute(sql)
        result = to_dataframe(relative_func(cursor.fetchall())).drop_duplicates()
        print(len(result))

        result.to_csv("./scrap_file/{0}_{1}.csv".format(relative_func.__name__, len(result)), encoding='utf-8-sig', index=None)
        func('forum_data', args).close()
        print('the total data extracting time is {0} sec'.format(round(time()-start_time, 3)))
