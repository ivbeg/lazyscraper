#!/usr/bin/env python
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
import lxml.html
import lxml.etree as etree
import click
from io import StringIO

DEFAULT_URL_FIELDS = ['_text', 'href']
DEFAULT_SELECT_FIELDS = ['_text', 'value']
TEXT_FIELD = "_text"
TAG_FIELD = "_tag"
DEFAULT_FIELDS = ['_tag', 'class', 'id', '_text']
URL_TAG_TYPES = ['href', 'src', 'srcset']

def __table_to_dict(node, strip_lf=True):
    """Extracts data from table"""
    data = []
    rows = node.xpath('./tbody/tr')
    if len(rows) == 0:
        rows = node.xpath('./tr')
    for row in rows:
        cells = []
        for cell in row.xpath('./td'):
            inner_tables = cell.xpath('./table')
            if len(inner_tables) < 1:
                text = cell.text_content()
                if strip_lf:
                    text = text.replace('\r',' ').replace('\n', ' ').strip()
                cells.append(text)
            else:
                cells.append([__table_to_dict(node, strip_lf) for t in inner_tables])
        data.append(cells)
    return data


def __taglist_to_dict(tags, fields, strip_lf=True):
    has_text = TEXT_FIELD in fields
    has_tag = TAG_FIELD in fields
    finfields = fields.copy()
    data = []
    if has_text: finfields.remove(TEXT_FIELD)
    if has_tag: finfields.remove(TAG_FIELD)
    for t in tags:
        item = {}
        if has_tag:
            item[TAG_FIELD] = t.tag
        if has_text:
            item[TEXT_FIELD] = t.text_content().strip()
            if strip_lf:
                item[TEXT_FIELD] = ' '.join(item[TEXT_FIELD].split())
        for f in finfields:
            item[f] = t.attrib[f] if f in t.attrib.keys() else ""
        data.append(item)
    return data


def pattern_extract_simpleul(tree, nodeclass, nodeid, fields):
    """Simple UL lists extractor pattern"""
    if nodeclass:
        xfilter = "//ul[@class='%s']/li//a" % (nodeclass)
    elif nodeid:
        xfilter = "//ul[@id='%s']/li//a" % (nodeid)
    else:
        xfilter = '//ul/li//a'
    tags = tree.xpath(xfilter)
    data = __taglist_to_dict(tags, fields)
    return data

def pattern_extract_simpleoptions(tree, nodeclass, nodeid, fields):
    """Simple SELECT / OPTIONS  extractor pattern"""
    if nodeclass:
        xfilter = "//select[@class='%s']/option" % (nodeclass)
    elif nodeid:
        xfilter = "//select[@id='%s']/option" % (nodeid)
    else:
        xfilter = '//select/option'
    tags = tree.xpath(xfilter)
    data = __taglist_to_dict(tags, fields)
    return data

def pattern_extract_exturls(tree, nodeclass, nodeid, fields):
    """Simple SELECT / OPTIONS  extractor pattern"""
    if nodeclass:
        xfilter = "//a[@class='%s']" % (nodeclass)
    elif nodeid:
        xfilter = "//a[@id='%s']" % (nodeid)
    else:
        xfilter = '//a'
    tags = tree.xpath(xfilter)
    filtered = []
    for t in tags:
        if 'href' in t.attrib.keys():
            if t.attrib['href'][:6] in ['http:/', 'https:']:
                filtered.append(t)
    data = __taglist_to_dict(filtered, fields)
    return data


def pattern_extract_forms(tree, nodeclass, nodeid, fields):
    """Extracts web forms from page"""
    res = []
    formattrlist = ['name', 'id', 'action', 'class', 'method']
    inputattrlist = ['name', 'id', 'type', 'class', 'value', 'src', 'size']
    textarealist = ['name', 'id', 'size', 'class']
    buttonlist = ['name', 'id', 'value', 'class']
    selectlist = ['name', 'id', 'multiple', 'size', 'class']
    optionlist = ['value', 'selected', 'class']
    tagnames = [('input', inputattrlist), ('textarea', textarealist), ('button', buttonlist), ('select', selectlist)]
    allforms = tree.xpath('//form')
    for form in allforms:
        fkey = {}
        for k in formattrlist:
            if form.attrib.has_key(k):
                fkey[k] = form.attrib[k]#
        for tag in form.iterdescendants():
            if not hasattr(tag, 'tag'): continue
            for tagname, tlist in tagnames:
                if tag.tag == tagname:
                    if not tagname in fkey.keys():   fkey[tagname] = []
                    tval = {'text' : tag.text}
                    for k in tlist:
                        if tag.attrib.has_key(k):
                            tval[k] = tag.attrib[k]
                    if tag.tag == 'select':
                        tval['options'] = []
                        options = tag.xpath('option')
                        for o in options:
                            optionval = {'text' : o.text}
#                            print o.text
                            for k in optionlist:
                                if o.attrib.has_key(k):
                                    optionval[k] = o.attrib[k]
                            tval['options'].append(optionval)
                    fkey[tagname].append(tval)
        res.append(fkey)
    return {'total' : len(res), 'list' : res}

PATTERNS = {
'simpleul' : {'func' : pattern_extract_simpleul, 'deffields' : DEFAULT_URL_FIELDS, 'json_only' : False },
'simpleopt' : {'func' : pattern_extract_simpleoptions, 'deffields' : DEFAULT_SELECT_FIELDS , 'json_only' : False },
'exturls' : {'func' : pattern_extract_exturls, 'deffields' : DEFAULT_URL_FIELDS, 'json_only' : False },
'getforms' : {'func' : pattern_extract_forms, 'deffields' : None, 'json_only' : True },
}


@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--xpath', default='//a', help='Xpath')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--absolutize', default=False, help='Absolutize urls')
@click.option('--format', default='text', help='Output format')
@click.option('--output', default=None, help='Output filename')
def extract(url, xpath, fieldnames, absolutize, format, output):
    """Extract data with xpath"""
    o = urlopen(url)
    rurl = o.geturl()
    data = o.read()
    root = lxml.html.fromstring(data)
    tree = root.getroottree()
    tags = tree.xpath(xpath)
    fields = fieldnames.split(',') if fieldnames else DEFAULT_FIELDS
    data = __taglist_to_dict(tags, fields)

    has_urltagtype = False
    for tagtype in URL_TAG_TYPES:
        if tagtype in fields:
            has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(data)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in data[i].keys(): continue
                if data[i][tagtype][:6] not in ['http:/', 'https:'] and len(data[i][tagtype]) > 0:
                    data[i][tagtype] = urljoin(rurl, data[i][tagtype])
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
    pass


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
@click.option('--output', default=None, help='Output filename')
def use(url, pattern, nodeid, nodeclass, fieldnames, absolutize, format, output):
    """Uses predefined pattern to extract page data"""
    o = urlopen(url)
    rurl = o.geturl()
    data = o.read()
    root = lxml.html.fromstring(data)
    tree = root.getroottree()

    pat = PATTERNS[pattern]
    fields = fieldnames.split(',') if fieldnames else pat['deffields']
    data = PATTERNS[pattern]['func'](tree, nodeclass, nodeid, fields)
    has_urltagtype = False
    if fields is not None:
        for tagtype in URL_TAG_TYPES:
            if tagtype in fields:
                has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(data)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in data[i].keys(): continue
                if data[i][tagtype][:6] not in ['http:/', 'https:'] and len(data[i][tagtype]) > 0:
                    data[i][tagtype] = urljoin(rurl, data[i][tagtype])
    # Instead error let's force json output if it's the only way
    if pat['json_only']: format = 'json'

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
@click.option('--output', default=None, help='Output filename')
def gettable(url, nodeid, nodeclass, fieldnames, format, output):
    """Extracts table with data from html"""
    o = urlopen(url)
    data = o.read()
    root = lxml.html.fromstring(data)
    tree = root.getroottree()
    if nodeclass:
        xfilter = "//table[@class='%s']" % (nodeclass)
    elif nodeid:
        xfilter = "//table[@id='%s']" % (nodeid)
    else:
        xfilter = '//table'
    tags = tree.xpath(xfilter)
    if len(tags) > 0:
        data = __table_to_dict(tags[0], strip_lf=True)
    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in data:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in data:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(data, sort_keys=True, indent=4 ))
    pass


cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()
