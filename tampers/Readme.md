
# How to make your own tamper script 

It's very simple ! you only need to create a function named "process" that takes **one** parameter in input and returns a single **string** *(Make sure it is not bytes)*. Then, if needed (ie, option -ut enabled), create a function "unprocess" that reverts the process of the payload.

for example:
```
#!/usr/bin/python3

from urllib.parse import quote, unquote

def process(payload):
    """
    Takes a payload in input
    :returns the string quoted
    """
    return quote(payload)

def process(payload):
    """
    Takes a string quoted in input
    :returns the string unquoted
    """
    return unquote(payload)
```