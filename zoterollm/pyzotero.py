import glob
import os
import sqlite3
from pyzotero import zotero
from collections import defaultdict
import pandas as pd
def zoteroapi():
    zotero_path = '/home/vankhoa@median.cad/snap/zotero-snap/common/Zotero/storage/'
    library_id = os.environ['ZOTERO_USER_ID']
    api_key = os.environ['ZOTERO_KEY']
    library_type = 'user'
    zot = zotero.Zotero(library_id, library_type, api_key)
    # items = zot.top(limit=5)
    # # we've retrieved the latest five top-level items in our library
    # # we can print each item's item type and ID
    # for item in items:
    #     print('Item: %s | Key: %s' % (item['data']['itemType'], item['data']['key']))

    collections = zot.all_collections()
    results = defaultdict(dict)
    nrows = 0
    for collection in collections:
        print('Collection: %s | Key: %s' % (collection['data']['name'], collection['data']['key']))
        items = zot.collection_items(collection['key'])
        for item in items:
            print('Item: %s | Key: %s' % (item['data']['itemType'], item['data']['key']))
            if 'filename' in item['data']:
                print(item['data']['filename'])
                path = zotero_path + '/' + item['data']['key'] + '/' + item['data']['filename']
                assert os.path.exists(path)
                results[nrows] = {
                    'key': item['data']['key'],
                    'collection': collection['data']['name'],
                    'path': path,
                    'type': 'pdf',
                }
            elif 'url' in item['data']:
                print(item['data']['url'])
                results[nrows] = {
                    'key': item['data']['key'],
                    'collection': collection['data']['name'],
                    'url': item['data']['url'],
                    'type': 'webpage',
                }
            else:
                raise NotImplementedError
            nrows += 1
    df = pd.DataFrame(results).T
    df.to_csv('zotero.csv', index=False)



def zotero_local():
    zotero_path = '/home/vankhoa@median.cad/snap/zotero-snap/common/Zotero/'
    # read sqlite file read-only
    # conn = sqlite3.connect(os.path.expanduser(f'file:{zotero_path}zotero.sqlite?mode=ro'),uri=True )
    # c = conn.cursor()
    # sql_query = """SELECT name FROM sqlite_master
    #   WHERE type='table';"""
    # c.execute(sql_query)
    # print(c.fetchall())
    # # c.execute('SELECT * FROM items')
    # # for row in c:
    # #     print(row)
    #
    # c.execute('SELECT * FROM itemDataValues')
    # for row in c:
    #     print(row)

    results = defaultdict(dict)
    nrows = 0
    pdf_files = glob.glob(zotero_path + 'storage/*/*.pdf')
    # html_files = glob.glob(zotero_path + 'storage/*/*.html')
    for pdf_file in pdf_files:
        pdf_file = pdf_file.replace(zotero_path, '')
        pdf_file = pdf_file.split('/')
        pdf_file = pdf_file[1]
        results[nrows] = {
            'pdf_file': pdf_file,
            'path': pdf_file,
        }
        nrows += 1


if __name__ == '__main__':
    zoteroapi()
    zotero_local()
