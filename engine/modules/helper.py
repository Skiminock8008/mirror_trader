import os
import sys
import json
from collections import deque

__DIR__ = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, __DIR__)
sys.path.insert(0, __DIR__ + '/../')


#
# Load data
#
def get_clients():
    file = open (__DIR__ + '/../../data/settings.json', 'r')
    file.seek(0)
    lines = file.readlines()
    data = '\n'.join(lines)

    obj = json.loads(data)

    return obj


def add_to_txt(value, exchange):
    with open(__DIR__ + '/../' + exchange + '/copy_clients.txt', 'a') as file:
        file.write(value['api_key'] + '   ')
        file.write(value['api_secret'] + '   ')
        file.write(value['net'] + '   ')
        file.write(value['name'] + '\n')


def list_clients(obj, exchange):
    open(__DIR__ + '/../' + exchange + '/copy_clients.txt', 'w').close()
    for attr, value in obj[exchange]['clients'].items():
        add_to_txt(value, exchange)
    open(__DIR__ + '/../' + exchange + '/main_account.txt', 'w').close()
    with open(__DIR__ + '/../' + exchange + '/main_account.txt', 'a') as file:
        file.write(obj[exchange]['main']['api_key'] + '   ')
        file.write(obj[exchange]['main']['api_secret'] + '   ')
        file.write(obj[exchange]['main']['net'])
    open(__DIR__ + '/../' + exchange + '/console_messages.txt', 'w').close()

def console_message(msg):
    print(msg)
    fname = __DIR__ + '/../bitmex/console_messages.txt'
    with open(fname, 'a') as file:
	    file.write(msg + '\n')
	    clearLines(fname)

def clearLines(infilepath):
    with open(infilepath) as infile: lines = deque(infile, 20)
    with open(infilepath, 'w') as outfile: outfile.write(''.join(lines))