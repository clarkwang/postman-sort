# Why

See the following discussions in the Postman project:

* https://github.com/postmanlabs/postman-app-support/issues/4253
* https://github.com/postmanlabs/postman-app-support/issues/5222

# What to sort

1. For Environments
   * Variables
1. For Collections
   * Variables
   * Folders (can be nested)
   * Requests
   * Requests' Params
   * Requests' Examples (including example's Params)

# How to use

1. In Postman, export a Collection or Environment to a JSON file (e.g. `unsorted.json`) in `v2.1` format.
1. Run

    ~~~
    python3 pm-sort.py unsorted.json > sorted.json
    # or
    python3 pm-sort.py < unsorted.json > sorted.json
    ~~~
    
1. In Postman, import `sorted.json`. (To be safe, choose `Import as Copy` when prompted.)
