
from sources.settings.COLORS import *

from datetime import datetime
from sources.utils import random_gen
from urllib.parse import urlparse

def get_date():
    """
    :returns a datetime object from now()
    """
    return datetime.now()

def makeURLCompliant(url):
    """
    Replace bad chars. We're not like requests, we don't urlencode EVERYTHING. Peace of sh*et.
    """
    # replace space, because It's not really URL compliant
    url = url.replace(' ', "%20")
    # replace "#" because if it's raw it's not gut
    url = url.replace("#", "%23")
    #"""
    #do something like
    # url = url.replace("/","%2f")
    #"""
    return url


def url_cleaner(url):
    """
    Takes url in input and reconstructs it with urllib parse to make it clean
    thus we remove the fragment & garbage things that doesn't look like urls
    add "?" or "&" at the end if it is needed
    :returns the url and the initials (provided) parameters
    """
    temp_url = urlparse(url)
    url = f"{temp_url.scheme}://{temp_url.netloc}{temp_url.path}?{temp_url.query}"
    return url

def color_triggers(trigger, values):
    time = values[0]
    length = values[1]
    diff = values[2]
    if trigger == "length_deny":
        values[1] = f"{color_green}{length}{color_end}"
    else:
        values[1] = f"{length}"
    if trigger == "timer":
        values[0] = f"{color_red}{time}{color_end}"
    else:
        values[0] = f"{time}"
    if diff:
        values[2] = f"{color_red}{diff}{color_end}"
    else:
        values[2] = f"{diff}"
    return values

def color_status(status):
    """
    Add some colors depending on the status returned
    :returns a string with some colors around it
    """
    status = str(status)
    if status[0] == str(5):
        status = f"{color_red}{status}{color_end}"
    elif status[0] == str(4) and status[2] != str(3):
        status = f"{color_yellow}{status}{color_end}"
    elif status == "403":
        status = f"{color_dark_blue}{status}{color_end}"
    elif status[0] == str(3):
        status = f"{color_light_blue}{status}{color_end}"
    else:
        status = f"{color_green}{status}{color_end}"
    return status
