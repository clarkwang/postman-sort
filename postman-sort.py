#!/usr/bin/env python3
# vi:set ts=8 sw=4 sta et:
#
# Author: Clark Wang <dearvoid at gmail.com>
#
#--------------------------------------------------------------------#

import json
import sys

def postman_sort(js):
    if not js or type(js) is not dict:
        return js

    items = js.get('item')
    if not items or type(items) is not list:
        return js

    for i in range(len(items) ):
        items[i] = postman_sort(items[i])

    js['item'] = sorted(items, key=lambda x: x['name'].lower() )

    return js

def main():
    if len(sys.argv) > 1:
        fp = open(sys.argv[1])
    else:
        fp = sys.stdin

    js = json.load(fp)
    js = postman_sort(js)
    json.dump(js, sys.stdout, sort_keys=False)

main()
