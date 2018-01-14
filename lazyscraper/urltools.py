# -*- coding: utf8 -*-
import json
import hashlib
import csv
import logging
import sys
from urllib.request import urlopen
from urllib.parse import urljoin
import requests
import lxml.html
import lxml.etree
from .consts import *
try:
    from bmemcached import Client
    from zlib import compress, decompress
except:
    pass

def get_cached_post(url, postdata, host='127.0.0.1', port=11211):
    """Returns url data from url with post request"""
    servers = ["%s:%d" % (host, port)]
    m = hashlib.sha256()
    m.update(url.encode('utf8'))
    m.update(str(postdata).encode('utf8'))
    key = m.hexdigest()
    client = Client(servers)
    c_data = client.get(key)
    if c_data:
        data = decompress(c_data)
    else:
        r = requests.post(url, postdata)
        data = r.text
        client.set(key, compress(data))
    hp = lxml.etree.HTMLParser(encoding='utf-8')
    root = lxml.html.fromstring(data, parser=hp)
    return root

def get_cached_url(url, timeout=DEFAULT_CACHE_TIMEOUT, host='127.0.0.1', port=11211):
    """Returns url data from url or from local memcached"""
    servers = ["%s:%d" % (host, port)]
    m = hashlib.sha256()
    m.update(url.encode('utf8'))
    key = m.hexdigest()
    client = Client(servers)
    c_data = client.get(key)
    if c_data:
        data = decompress(c_data)
    else:
        o = urlopen(url)
        rurl = o.geturl()
        data = o.read()
        client.set(key, compress(data))
    hp = lxml.etree.HTMLParser(encoding='utf-8')
    root = lxml.html.fromstring(data, parser=hp)
    return root
