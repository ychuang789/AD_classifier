import logging
import pymysql.cursors
import pandas as pd
from time import time
from tqdm import tqdm

def connect_database(db):
    try:
        config = {
            'host':'172.18.20.190',
            'user':'rd2',
            'password':'eland4321',
            'db':db,
            'charset':'utf8mb4',
            'cursorclass':pymysql.cursors.DictCursor,
        }
        connection = pymysql.connect(**config)
        return connection

    except:
        logging.error('Fail to connect to database.')

def find_keyword(data):
    with open('keyword.txt', 'r') as f:
        keyword = [line for line in f.read().splitlines()]

    save = []
    for item in tqdm(data):
        for word in keyword:
            if word not in list(item.values())[0] + ' ' + list(item.values())[1]:
                save.append(item)
                continue

    return save

def find_without_keyword(data):
    with open('keyword.txt', 'r') as f:
        keyword = [line for line in f.read().splitlines()]

    save_wk = []
    for item in tqdm(data):
        if any([x in (list(item.values())[0] + list(item.values())[1]) for x in keyword]):
            continue
        else:
            save_wk.append(item)

    return save_wk

def to_dataframe(data):
    return pd.DataFrame.from_dict(data)

if __name__ == "__main__":
    start_time = time()
    func = connect_database
    relative_func = find_keyword
    number = 2000
    with func('forum_data').cursor() as cursor:
        sql = "SELECT title, content FROM ts_page_content LIMIT {0}".format(number)
        cursor.execute(sql)
        result = to_dataframe(relative_func(cursor.fetchall())).drop_duplicates()
        print(len(result))

        result.to_csv("{0}_{1}.csv".format(relative_func.__name__, len(result)), encoding='utf-8-sig', index=None)

        # with open("data_{0}.json".format(len(result)), "w", encoding='utf8') as file:
        #     json.dump(result, file, default=str, ensure_ascii=False)
        # file.close()

        func('forum_data').close()
        print('the total data extracting time is {0} sec'.format(round(time()-start_time, 3)))
