#!/usr/bin/python3

from urllib.parse import quote, unquote

def process(payload):
    return quote(payload)

def unprocess(payload):
    return unquote(payload)