#!/usr/bin/python3

from base64 import b64encode, b64decode

def process(payload):
    if not isinstance(payload, bytes):
        return b64encode(payload.encode("utf-8")).decode("utf8")
    else:
         return b64encode(payload).decode("utf8")

def unprocess(payload):
    if not isinstance(payload, bytes):
        return b64decode(payload.encode("utf-8")).decode("utf8")
    else:
         return b64decode(payload).decode("utf8")