from lxml import etree
from io import BytesIO


def parse_plist_etree(xml_bytes):
    def parse_element(el):
        tag = el.tag
        if tag == 'dict':
            result = {}
            it = iter(el)
            for key in it:
                val = next(it)
                if key.text == 'dvfm_states':
                    continue
                result[key.text] = parse_element(val)
            return result
        elif tag == 'array':
            return [parse_element(child) for child in el]
        elif tag == 'string':
            return el.text or ''
        elif tag == 'integer':
            return int(el.text)
        elif tag == 'real':
            return float(el.text)
        elif tag == 'true':
            return True
        elif tag == 'false':
            return False
        elif tag == 'data':
            return el.text.encode('utf-8') if el.text else b''
        elif tag == 'date':
            return el.text

    plist = etree.fromstring(xml_bytes)
    if plist.tag != 'plist':
        raise ValueError("Not a valid plist")

    return parse_element(plist[0])
