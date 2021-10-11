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
from types import SimpleNamespace

class NsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleNamespace):
            return self.encode_hook(obj)
        else:
            # should not reach here
            return super().default(obj)

    # obj --> dict
    @staticmethod
    def encode_hook(obj):
       #assert isinstance(obj, SimpleNamespace)
        return obj.__dict__

class NsDecoder(json.JSONDecoder):
    def decode(self, s):
        return json.JSONDecoder(object_hook=self.decode_hook).decode(s)

    # obj <-- { 'k1': 'v1', 'k2': 'v2', ... }
    @staticmethod
    def decode_hook(d):
        return SimpleNamespace(**d)

    # obj <-- [('k1', 'v1'), ('k2', 'v2'), ...]
    @staticmethod
    def decode_pairs_hook(pairs):
        d = dict(pairs)
        return NsDecoder.decode_hook(d)

def hasattr_dotted(obj, attrs):
    for attr in attrs.split('.'):
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
        else:
            return False

    return True

def getattr_dotted(obj, attrs, default=None):
    assert attrs

    for attr in attrs.split('.'):
        if hasattr(obj, attr):
            obj = getattr(obj, attr)
        else:
            return default
    else:
        return obj

# sort request's query params
def postman_sort_req(req):
    if not req:
        return req
    if not hasattr_dotted(req, 'url.query'):
        return req

    queries = req.url.query
    # 'key' may be null.
    queries.sort(key=lambda x: (x.key or '').lower() )

    req.url.query = queries
    return req

# sort responses and responses' query params
def postman_sort_resp(resps):
    if not resps:
        return resps

    resps.sort(key=lambda x: x.name.lower() )

    for resp in resps:
        if hasattr_dotted(resp, 'originalRequest.url.query'):
            queries = resp.originalRequest.url.query
            queries.sort(key=lambda x: (x.key or '').lower() )

            resp.originalRequest.url.query = queries
    return resps

def postman_sort(js, _level=1):
    if not js or type(js) is not SimpleNamespace:
        return js

    items = js.item
    if not items or type(items) is not list:
        return js

    for i in range(len(items) ):
        item = items[i]
        if hasattr(item, 'item'):
            # folders (may be nested) under the collection
            items[i] = postman_sort(item, _level=_level + 1)
        else:
            # requests
            if hasattr(item, 'request'):
                req = item.request
                item.request = postman_sort_req(req)
            # example responses
            if hasattr(item, 'response'):
                resps = item.response
                item.response = postman_sort_resp(resps)
            items[i] = item

    js.item = sorted(items, key=lambda x: x.name.lower() )

    # collection variables
    if _level == 1 and getattr(js, 'variable', None):
        assert type(js.variable) is list
        js.variable.sort(key=lambda x: x.key if x.key.isupper() else x.key.lower() )

    return js

def postman_sort_env(js):
    js.values.sort(key=lambda x: x.key if x.key.isupper() else x.key.lower() )
    return js

def main():
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    else:
        fp = sys.stdin

    js = json.load(fp, cls=NsDecoder)
    dump_before = json.dumps(js, cls=NsEncoder)

    # Postman environment
    if getattr(js, '_postman_variable_scope', '') == 'environment':
        js = postman_sort_env(js)

        # Postman collection
    elif '/collection/v2.1.0/' in getattr_dotted(js, 'info.schema', ''):
        # https://schema.getpostman.com/json/collection/v2.1.0/collection.json
        js = postman_sort(js)
    else:
        raise Exception('unknown format: neither collection nor environment')

    dump_after = json.dumps(js, cls=NsEncoder)
    assert len(dump_before) == len(dump_after)

    print(dump_after)

main()
