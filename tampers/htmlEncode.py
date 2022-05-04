#!/usr/bin/python3

from html import escape, unescape

def process(payload):
    return escape(payload)

def unprocess(payload):
    return unescape(payload)