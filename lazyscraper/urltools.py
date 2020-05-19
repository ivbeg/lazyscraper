# -*- coding: utf8 -*-
import json
import hashlib
import csv
import logging
import sys
from urllib.request import urlopen
from urllib.parse import urljoin, quote, urlsplit, urlunsplit
import requests
import lxml.html
import lxml.etree
from .consts import *
try:
    from bmemcached import Client
    from zlib import compress, decompress
except:
    pass

import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def get_cached_post(url, postdata, host=None, port=11211, agent=DEFAULT_USER_AGENT):
    """Returns url data from url with post request"""
    servers = ["%s:%d" % (host, port)]
    m = hashlib.sha256()
    m.update(url.encode('utf8'))
    m.update(str(postdata).encode('utf8'))
    key = m.hexdigest()
#    client = Client(servers)
#    c_data = client.get(key)
#    if c_data:
#        data = decompress(c_data)
#    else:
    r = requests.post(url, postdata, headers={'User-Agent' : agent})
    data = r.text
#        client.set(key, compress(data))
    hp = lxml.etree.HTMLParser()
    root = lxml.html.fromstring(data, parser=hp)
    return root

def get_cached_url(url, timeout=DEFAULT_CACHE_TIMEOUT, host=None, port=11211, agent=DEFAULT_USER_AGENT):
    """Returns url data from url or from local memcached"""
    c_data = None
    client = None
    if host is not None:
        servers = ["%s:%d" % (host, port)]
        m = hashlib.sha256()
        m.update(url.encode('utf8'))
        key = m.hexdigest()
        try:
            client = Client(servers)
            c_data = client.get(key)
        except NameError as ex:
            pass
    if c_data:
        data = decompress(c_data)
    else:
        o = requests.get(url, headers={'User-Agent' : agent})
        if client is not None:
            client.set(key, compress(o.text))
    hp = lxml.etree.HTMLParser()
    root = lxml.html.fromstring(o.text, parser=hp)
    return root
