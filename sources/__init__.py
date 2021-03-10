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
    intruder.set_method("POST")
    # set the payload file
    intruder.set_payloadfile("%%DATABASE%%/fuzz1.txt", offset=0)
    # or use
    #intruder.set_distant_payloadfile("http://somewebsite/", offset=0)
    # or use
    #intruder.set_regex_payload(r"[a-z]{5}", offset=0)
    # OPTIONNAL: shuffle the payloads
    intruder.shuffle_payload_list()

    # OPTIONNAL: define changes to the payloads
    intruder.set_mutations(r'.js', ".js.zip")
    intruder.set_mutations(r'.php',r'.php[0-7]{1}')

    # OPTIONNAL: use a tamperscript
    intruder.use_tamper("base64")

    # OPTIONNAL: define the getter for the results
    # status_filters : ["200"] or can be range ["200-300"] or ["200-&"]
    # length_filter : ["1540","0-999"]
    # length_exclusion : ["1420"]
    # time_filter : ["15-&"]

    intruder.set_getter(status_filter=["any"], length_filter=["any"],\
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
    intruder.run(threads=5, verbosity=3)
    print(intruder.results())
