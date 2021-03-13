#!/usr/bin/python3

from sources.core import Supptruder
from sources.settings.COLORS import *

__version__ = "2.0"
__author__ = "Sicarius (@AMTraaaxX)"

def main():
    """
    Main process of supptruder
    """
    print(f"\n{color_banner}~~ Supp'Truder v{__version__}, made with love by {__author__} ~~{color_end}")
    intruder = Supptruder()

    # change the replace_string caracter that will be used later
    intruder.change_replace_string("§")
    # init target with optional params
    intruder.set_target("https://elsicarius.fr/§",\
     base_payload="FuzzingYourApp", data=None, base_request_match=False,\
     ignore_base_request=False)

    # OPTIONNAL: specify a different method
    intruder.set_method("GET")
    # set the payload file
    intruder.set_payloadfile("%%DATABASE%%/fuzz1.txt", offset=0)
    # or use
    #intruder.set_distant_payloadfile("http://somewebsite/", offset=0)
    # or use
    #intruder.set_regex_payload(r"[a-z]{5}", offset=0)
    # OPTIONNAL: shuffle the payloads
    intruder.shuffle_payload_list()

    # OPTIONNAL: define changes to the payloads
    # use del_original=True if you wan to remove the occurences not modified
    # don't forget these are regex ! "." != actual "." but means "any caracter"

    intruder.set_mutations(r'\.js', r"\.js\.zip", del_original=False)
    intruder.set_mutations(r'\.php',r'\.php[0-3]{1}', del_original=False)
    intruder.set_mutations(r'\.html',r'\.html[0-1]{1}', del_original=False)

    # OPTIONNAL: use a tamperscript
    """
    intruder.use_tamper("base64")"""

    # OPTIONNAL: define the getter for the results
    # filters folow the rules: ['singlevalue', 'min-max']
    # single_value can be : 200 or n200 or 50x or n50x
    # cannot be: 5xx or 5n02 sorry :(
    # n means "not" and x means "any"
    # status_filters : ["200"] or can be range ["200-300"] or ["200-&"]
    # length_filter : ["1540","0-999"]
    # length_exclusion : ["1420"]
    # time_filter : ["15-&"]

    intruder.set_getter(status_filter=["n50x"], length_filter=[],\
                    length_exclusion=[], time_filter=[])

    # OPTIONNAL: update the settings for the requests
    intruder.customize_requests(timeout=20, allow_redirects=False,\
                    throttle=0.01, headers={})

    # OPTIONNAL: customize the diff lib

    intruder.customize_difflib(use_quick_ratio=True, difference_timer=2000,\
                                minimum_text_difference=0.99)

    # OPTIONNAL: set logfile
    intruder.save_logs(open("mylogfile", "a+"))

    # run the intruder
    intruder.run(threads=3, verbosity=3)
    print(intruder.results())
