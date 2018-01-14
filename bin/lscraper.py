#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Lazy scraping tool"""
import json
import os
import hashlib
import zlib
import time
import csv
import logging
import datetime
import io
import sys
from urllib.request import urlopen
from urllib.parse import urljoin
import requests
import lxml.html
import lxml.etree
import click
from io import StringIO
try:
    from bmemcached import Client
    from zlib import compress, decompress
except:
    pass

from lazyscraper.consts import DEFAULT_FIELDS
from lazyscraper.scraper import  use_pattern, extract_data_xpath, get_table
from lazyscraper.patterns import PATTERNS

#logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)



@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--xpath', default='//a', help='Xpath')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--absolutize', default=False, help='Absolutize urls')
@click.option('--post', default=False, help='Use post request')
@click.option('--pagekey', default=False, help='Pagination url/post parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--format', default='text', help='Output format')
@click.option('--output', default=None, help='Output filename')
def extract(url, xpath, fieldnames, absolutize, post, pagekey, pagerange, format, output):
    """Extract data with xpath"""
    fields = fieldnames.split(',') if fieldnames else DEFAULT_FIELDS
    data = extract_data_xpath(url, xpath, fieldnames, absolutize, post, pagekey, pagerange)
    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(data, indent=4 ))

@click.group()
def cli2():
    pass

@cli2.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--pattern', default='simpleul', help='Scraper pattern')
@click.option('--nodeid', default=None, help='Node id in html')
@click.option('--nodeclass', default=None, help='Node "class" in html')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--absolutize', default=False, help='Absolutize urls')
@click.option('--format', default='text', help='Output format')
@click.option('--pagekey', default=False, help='Pagination url parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--output', default=None, help='Output filename')
def use(url, pattern, nodeid, nodeclass, fieldnames, absolutize, format, pagekey, pagerange, output):
    """Uses predefined pattern to extract page data"""
    pat = PATTERNS[pattern]
    fields = fieldnames.split(',') if fieldnames else pat['deffields']
    findata = use_pattern(url, pattern, nodeid, nodeclass, fieldnames, absolutize, pagekey, pagerange)

    if pat['json_only']: format = 'json'

    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in findata:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in findata:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(findata, indent=4 ))
    pass


@click.group()
def cli3():
    pass

@cli3.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--nodeid', default=None, help='Node id in html')
@click.option('--nodeclass', default=None, help='Node "class" in html')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--format', default='text', help='Output format')
@click.option('--pagekey', default=False, help='Pagination url parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--output', default=None, help='Output filename')
def gettable(url, nodeid, nodeclass, fieldnames, format, pagekey, pagerange, output):
    """Extracts table with data from html"""
    findata = get_table(url, nodeid, nodeclass, fieldnames, pagekey, pagerange)

    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in findata:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in findata:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(findata, sort_keys=True, indent=4 ))
    pass


cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()
