import os
import sys
import json


__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')
#
# Load data
#

def get_clients():
    file = open (__DIR__ + '/../../data/settings.json', 'r', encoding='utf-8')
    file.seek(0)
    lines = file.readlines()
    data = '\n'.join(lines)

    obj = json.loads(data)

    return obj


def add_to_txt(value, exchange):
    with open(__DIR__ + '/../bitmex/copy_clients.txt', 'a') as file:
        file.write(value['api_key'] + '   ')
        file.write(value['api_secret'] + '   ')
        file.write('testnet' + '   ')
        file.write(value['name'] + '\n')


def list_clients(obj, exchange):
    open(__DIR__ + '/../bitmex/copy_clients.txt', 'w').close()
    for attr, value in obj[exchange]['clients'].items():
        add_to_txt(value, exchange)
    open(__DIR__ + '/../bitmex/main_account.txt', 'w').close()
    with open(__DIR__ + '/../bitmex/main_account.txt', 'a') as file:
        file.write(obj[exchange]['main']['api_key'] + '   ')
        file.write(obj[exchange]['main']['api_secret'] + '   ')
        file.write('testnet')
