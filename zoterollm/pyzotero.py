from dotenv import load_dotenv
load_dotenv()
import glob
import os
import sqlite3
from pyzotero import zotero
from collections import defaultdict
import argparse
import pandas as pd
from pathlib import Path


def zoteroapi(zotero_path=None):
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
    df.to_csv(Path(os.environ['working_dir']) / 'zotero.csv', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--zoteropath', type=str,
                        help='path to zotero storage')
    args = parser.parse_args()

    os.makedirs(os.environ['working_dir'], exist_ok=True)

    zoteroapi(zotero_path=args.zoteropath)
