#!/usr/bin/python
__author__ = "Justin Stals"

import sys
import json
import time
import re
import requests
from requests.auth import HTTPBasicAuth

api_key = ''
endpoint_base = 'https://api.crunchbase.com/v3.1/'
headers = {'Content-Type': 'application/json'}

def get_crunchbase_org(name, uuid):
    try:
        odm = get_odm(name, uuid)
    except TypeError:
        pass
    if odm:
        return odm['properties']
    else:
        return None

def get_odm(name, uuid):

    call = f'{endpoint_base}odm-organizations?query={name}&user_key={api_key}'

    response = get(call)
    if not response:
        return None

    paging = response['data']['paging']
    num_pages = paging['number_of_pages']
    next_page_url = paging['next_page_url']

    uuid_search = uuid.replace('-', '')

    items = response['data']['items']

    for item in items:
        if item['uuid'] == uuid_search:
            return item

    for i in range(2, num_pages):
        item = get_odm_worker(str(i), name, uuid_search)
        if item:
            return item
    
    return None

def get_odm_worker(page_num, name, uuid):

    call = f'{endpoint_base}organizations?page={page_num}&sort_order=custom&items_per_page=100&query={name}&user_key={api_key}'
    response = get(call)

    items = response['data']['items']

    if not items: return None

    for item in items:
        if item['uuid'] == uuid.replace('-', ''):
            return item
    for i in range(2, num_pages):
        item = get_odm_loop(str(i), name, uuid)
        if item:
            return item

# API call
def get(call):
    r = requests.get(call)
    if check_err(r):
        return None
    return r.json()

# Handle errors
def check_err(r):
    if r.status_code != 200:
        if '<' in r.text:
            error_msg = re.search(r'<h1>(.*?)</h1>', r.text).group(1)
        else:
            error_msg = r.text
        print(f'Error: {error_msg}')
        return True
    else:
        return False