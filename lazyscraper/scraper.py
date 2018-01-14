#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
from urllib.parse import urljoin

from .consts import *
from .htmltools import taglist_to_dict, table_to_dict
from .urltools import get_cached_url, get_cached_post
from .patterns import  PATTERNS

#logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

def extract_data_xpath(url, xpath, fieldnames=None, absolutize=False, post=None, pagekey=False, pagerange=False):
    """Extract data with xpath

    :param url:
        HTML webpage url
    :type url: str|unicode
    :param xpath:
        xpath expression
    :type xpath: str|unicode
    :param fieldnames:
        string with list of fields like "src,alt,href,_text"
    :type fieldnames: str|unicode
    :param absolutize:
        Absolutize all urls returned as href and other url-like fields
    :type absoultize: bool
    :param post:
        If True use POST for HTTP requests
    :type post: bool
    :param pagekey:
        Key of the page listing. GET or POST parameter
    :type pagekey: str|unicode
    :param pagerange:
        Range of pages to process. String with format 'min,max,step', example: '1,72,1'
    :type pagerange: str|unicode


    :return: Returns array of extracted values
    :rtype: :class:`array`."""

    fields = fieldnames.split(',') if fieldnames else DEFAULT_FIELDS
    data = []
    if pagekey is False:
        if post:
            root = get_cached_post(url)
        else:
            root = get_cached_url(url)
        tree = root.getroottree()
        tags = tree.xpath(xpath)
        data = taglist_to_dict(tags, fields)
    else:
        start, end, step, pagesize = map(int, pagerange.split(','))
#        for i in range(start, end, step):
        current = start
        while True:
            anurl = url + '?%s=%d' % (pagekey,current)
            logging.info('Processing url %s' % (anurl))
            if post:
                root = get_cached_post(anurl, {pagekey : str(current)})
            else:
                root = get_cached_url(anurl)
            tree = root.getroottree()
            tags = tree.xpath(xpath)
#            print(tags)
            items = taglist_to_dict(tags, fields)
            data.extend(items)
            current += 1
            if pagesize != -1 and len(items) < pagesize:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break
            if end != -1 and current == end+1:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break

    has_urltagtype = False
    for tagtype in URL_TAG_TYPES:
        if tagtype in fields:
            has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(data)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in data[i].keys(): continue
                if data[i][tagtype][:6] not in ['http:/', 'https:'] and len(data[i][tagtype]) > 0:
                    data[i][tagtype] = urljoin(url, data[i][tagtype])
    return data


def use_pattern(url, pattern, nodeid=None, nodeclass=None, fieldnames=None, absolutize=False, pagekey=False, pagerange=False):
    """Uses predefined pattern to extract page data
    :param url:
        HTML webpage url
    :type url: str|unicode
    :param nodeid:
        id key for nodes
    :type nodeid: str|unicode
    :param nodeclass:
        class key for nodes
    :type nodeclass: str|unicode
    :param fieldnames:
        string with list of fields like "src,alt,href,_text"
    :type fieldnames: str|unicode
    :param absolutize:
        Absolutize all urls returned as href and other url-like fields
    :type absoultize: bool
    :param pagekey:
        Key of the page listing. GET or POST parameter
    :type pagekey: str|unicode
    :param pagerange:
        Range of pages to process. String with format 'min,max,step', example: '1,72,1'
    :type pagerange: str|unicode

    :return: Returns array of extracted values
    :rtype: :class:`array`."""
    findata = []
    pat = PATTERNS[pattern]
    fields = fieldnames.split(',') if fieldnames else pat['deffields']

    if pagekey is False:
        root = get_cached_url(url)
        tree = root.getroottree()
        findata = PATTERNS[pattern]['func'](tree, nodeclass, nodeid, fields)
    else:
        start, end, step = map(int, pagerange.split(','))
        for i in range(start, end, step):
            anurl = url + '?%s=%d' % (pagekey,i)
#            print('Processing url %s' % (anurl))
            root = get_cached_url(url)
            tree = root.getroottree()
            findata.extend(PATTERNS[pattern]['func'](tree, nodeclass, nodeid, fields))

    has_urltagtype = False
    if fields is not None:
        for tagtype in URL_TAG_TYPES:
            if tagtype in fields:
                has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(findata)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in findata[i].keys(): continue
                if findata[i][tagtype][:6] not in ['http:/', 'https:'] and len(findata[i][tagtype]) > 0:
                    findata[i][tagtype] = urljoin(url, findata[i][tagtype])
    return findata


def get_table(url, nodeid=None, nodeclass=None, pagekey=False, pagerange=False):
    """Extracts table with data from html
     :param url:
         HTML webpage url
     :type url: str|unicode
     :param nodeid:
         id key for nodes
     :type nodeid: str|unicode
     :param nodeclass:
         class key for nodes
     :type nodeclass: str|unicode
     :param pagekey:
         Key of the page listing. GET or POST parameter
     :type pagekey: str|unicode
     :param pagerange:
         Range of pages to process. String with format 'min,max,step', example: '1,72,1'
     :type pagerange: str|unicode

     :return: Returns array of extracted values
     :rtype: :class:`array`."""

    if pagekey is False:
        root = get_cached_url(url)
        tree = root.getroottree()
        if nodeclass:
            xfilter = "//table[@class='%s']" % (nodeclass)
        elif nodeid:
            xfilter = "//table[@id='%s']" % (nodeid)
        else:
            xfilter = '//table'
        tags = tree.xpath(xfilter)
        if len(tags) > 0:
            findata = table_to_dict(tags[0], strip_lf=True)
        else:
            findata = []
    else:
        findata = []
        start, end, step, pagesize = map(int, pagerange.split(','))
#        for i in range(start, end, step):
        current = start
        while True:
            anurl = url + '?%s=%d' % (pagekey,current)
            logging.info('Crawling url %s' % (anurl))
            root = get_cached_url(anurl)
            logging.info('Got url %s' % (anurl))
            tree = root.getroottree()
            if nodeclass:
                xfilter = "//table[@class='%s']" % (nodeclass)
            elif nodeid:
                xfilter = "//table[@id='%s']" % (nodeid)
            else:
                xfilter = '//table'
            tags = tree.xpath(xfilter)
            if len(tags) > 0:
                items = table_to_dict(tags[0], strip_lf=True)
                findata.extend(items)
            else:
                items = []

            current += 1
            if pagesize != -1 and len(items) < pagesize:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break
            if end != -1 and current == end+1:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break
    return findata

