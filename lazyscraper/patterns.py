# -*- coding: utf8 -*-
from .consts import *
from .htmltools import table_to_dict, taglist_to_dict

def pattern_extract_simpleul(tree, nodeclass, nodeid, fields):
    """Simple UL lists extractor pattern"""
    if nodeclass:
        xfilter = "//ul[@class='%s']/li//a" % (nodeclass)
    elif nodeid:
        xfilter = "//ul[@id='%s']/li//a" % (nodeid)
    else:
        xfilter = '//ul/li//a'
    tags = tree.xpath(xfilter)
    data = taglist_to_dict(tags, fields)
    return data

def pattern_extract_simpleoptions(tree, nodeclass, nodeid, fields):
    """Simple SELECT / OPTION  extractor pattern"""
    if nodeclass:
        xfilter = "//select[@class='%s']/option" % (nodeclass)
    elif nodeid:
        xfilter = "//select[@id='%s']/option" % (nodeid)
    else:
        xfilter = '//select/option'
    tags = tree.xpath(xfilter)
    data = taglist_to_dict(tags, fields)
    return data

def pattern_extract_exturls(tree, nodeclass, nodeid, fields):
    """Pattern to extract external urls"""
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
    data = taglist_to_dict(filtered, fields)
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
