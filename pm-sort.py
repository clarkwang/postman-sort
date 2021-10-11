#!/usr/bin/env python3
# vi:set ts=8 sw=4 sta et:
#
# Author: Clark Wang <dearvoid at gmail.com>
#
# Note:
#  - Use v2.1 format when exporting Postman data.
#  - Folders in a collection can be _nested_.
#
#--------------------------------------------------------------------#

import json
import sys

def dichain_has(d, dotted):
    keys = dotted.split('.')
    assert keys and all(keys)

    for key in keys:
        if type(d) is not dict:
            return False
        if key not in d:
            return False
        else:
            d = d.get(key)
    return True

def dichain_get(d, dotted):
    keys = dotted.split('.')
    assert keys and all(keys)

    for key in keys:
        if type(d) is not dict:
            return None
        if key not in d:
            return None
        else:
            d = d.get(key)
    return d

def dichain_set(d, dotted, value):
    keys = dotted.split('.')
    assert keys and all(keys)

    saved = d
    for key in keys[:-1]:
        assert type(d) is dict and key in d
        d = d[key]

    assert type(d) is dict
    d[keys[-1]] = value

    return saved

# sort request's query params
def postman_sort_req(req):
    if not req:
        return req
    if not dichain_has(req, 'url.query'):
        return req

    queries = dichain_get(req, 'url.query')
    queries.sort(key=lambda x: x['key'].lower() )

    dichain_set(req, 'url.query', queries)
    return req

# sort responses and responses' query params
def postman_sort_resp(resps):
    if not resps:
        return resps

    resps.sort(key=lambda x: x['name'].lower() )

    for resp in resps:
        if dichain_has(resp, 'originalRequest.url.query'):
            queries = dichain_get(resp, 'originalRequest.url.query')
            queries.sort(key=lambda x: x['key'].lower() )

            dichain_set(resp, 'originalRequest.url.query', queries)
    return resps

def postman_sort(js):
    if not js or type(js) is not dict:
        return js

    items = js.get('item')
    if not items or type(items) is not list:
        return js

    for i in range(len(items) ):
        item = items[i]
        if 'item' in item:
            # folders (may be nested) under the collection
            items[i] = postman_sort(item)
        else:
            # requests
            if 'request' in item:
                req = item['request']
                item['request'] = postman_sort_req(req)
            # example responses
            if 'response' in item:
                resps = item['response']
                item['response'] = postman_sort_resp(resps)
            items[i] = item

    js['item'] = sorted(items, key=lambda x: x['name'].lower() )

    return js

def main():
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    else:
        fp = sys.stdin

    if 1:
        data = fp.read()
        assert 'json/collection/v2.1' in data
        js = json.loads(data)
    else:
        js = json.load(fp)

    dump_before = json.dumps(js)

    js = postman_sort(js)
    dump_after = json.dumps(js)

    assert len(dump_before) == len(dump_after)

    if 1:
        print(dump_after)
    else:
        json.dump(js, sys.stdout, sort_keys=False)

main()
