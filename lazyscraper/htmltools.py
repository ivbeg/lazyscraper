# -*- coding: utf8 -*-
from .consts import *

def table_to_dict(node, strip_lf=True):
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
                text = u' '.join(cell.itertext()) #cell.text_content()
                if strip_lf:
                    text = text.replace(u'\r',u' ').replace(u'\n', u' ').strip()
                cells.append(text)
            else:
                cells.append([table_to_dict(node, strip_lf) for t in inner_tables])
        data.append(cells)
    return data


def taglist_to_dict(tags, fields, strip_lf=True):
    """Converts list of tags into dict"""
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
            item[TEXT_FIELD] = ' '.join(t.itertext()).strip()
            if strip_lf:
                item[TEXT_FIELD] = (' '.join(item[TEXT_FIELD].split())).strip()
        for f in finfields:
            item[f] = t.attrib[f].strip() if f in t.attrib.keys() else ""
        data.append(item)
    return data

