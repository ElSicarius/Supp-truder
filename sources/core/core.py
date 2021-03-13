
from . import session
from sources.intruder import Intruder
from sources.selfhttp import DiffLibrary
from sources.utils import random_gen_from_regex, clean_bytes, clear_url, clean_end_parameters
from sources.settings.COLORS import *

class Supptruder():
    """ brain of Supp'truder"""
    def __init__(self):
        self.SESSION = session.Session()
        self.intruder = Intruder(self.SESSION)
        return

    def change_replace_string(self, string):
        self.SESSION.Conf.settings_["PROGRAM"].program_replace_string = string

    # init target with optional params
    def set_target(self, target, base_payload="FuzzingYourApp", data=None,\
        base_request_match=False, ignore_base_request=False):
        self.SESSION.Conf.settings_["PROGRAM"].program_target = target
        self.SESSION.Conf.settings_["PROGRAM"].program_base_payload = base_payload
        self.SESSION.Conf.settings_["PROGRAM"].program_raw_data = data
        self.SESSION.Conf.settings_["DIFFLIB"].difflib_base_request_match = base_request_match
        self.SESSION.Conf.settings_["DIFFLIB"].difflib_ignore_base_request = ignore_base_request

    # set the payload file
    def set_payloadfile(self, payload_file_path, offset=0):
        self.SESSION.Conf.settings_["FILES"].files_wordlist = payload_file_path
        self.SESSION.Conf.settings_["PROGRAM"].wordlist_offset = offset

    # or use
    def set_distant_payloadfile(self, distant_wordlist, offset=0):
        self.SESSION.Conf.settings_["FILES"].files_distant_wordlist = distant_wordlist
        self.SESSION.Conf.settings_["PROGRAM"].wordlist_offset = offset

    def set_method(self, method):
        if method != "GET":
            self.SESSION.Conf.settings_["REQUEST"].request_method = method

    # or use
    def set_regex_payload(self, regex, offset=0):
        self.SESSION.Conf.settings_["PROGRAM"].program_regex_wordlist = regex
        self.SESSION.Conf.settings_["PROGRAM"].wordlist_offset = offset

    # OPTIONNAL: shuffle the payloads
    def shuffle_payload_list(self):
        self.SESSION.Conf.settings_["PROGRAM"].wordlist_shuffle = True


    # OPTIONNAL: define changes to the payloads
    def set_mutations(self, regex1, regex2, del_original=False):
        self.SESSION.Conf.settings_["PROGRAM"].wordlist_mutations.append((regex1, regex2, del_original))

    # OPTIONNAL: use a tamperscript
    def use_tamper(self, tampername):
        self.SESSION.Conf.settings_["PROGRAM"].program_tamper = tampername

    def set_getter(self, status_filter=["any"], length_filter=["any"],\
            length_exclusion=[], time_filter=[]):
        self.SESSION.Conf.settings_["PROGRAM"].program_status_filter = status_filter
        self.SESSION.Conf.settings_["PROGRAM"].program_length_filter = length_filter
        self.SESSION.Conf.settings_["PROGRAM"].program_length_exclusion = length_exclusion
        self.SESSION.Conf.settings_["PROGRAM"].program_time_filter = time_filter

    # OPTIONNAL: update the settings for the requests
    def customize_requests(self, timeout=20, allow_redirects=False,\
                    throttle=0.01, headers={}):
        self.SESSION.Conf.settings_["REQUEST"].request_timeout = timeout
        self.SESSION.Conf.settings_["REQUEST"].request_allow_redirects = allow_redirects
        self.SESSION.Conf.settings_["REQUEST"].request_throttle = throttle
        self.SESSION.Conf.settings_["REQUEST"].request_base_headers.update(headers)

    # OPTIONNAL: customize the diff lib

    def customize_difflib(self, use_quick_ratio=True, difference_timer=2000,\
                                minimum_text_difference=None):
        self.SESSION.Conf.settings_["DIFFLIB"].difflib_quick_ratio = use_quick_ratio
        self.SESSION.Conf.settings_["DIFFLIB"].difflib_difference = minimum_text_difference
        self.SESSION.Conf.settings_["DIFFLIB"].difflib_difftimer = difference_timer

    # OPTIONNAL: set logfile
    def save_logs(self, logfile_handler):
        self.SESSION.Conf.settings_["FILES"].files_output_log_var = logfile_handler

    # run the intruder
    def run(self, threads=5, verbosity=3):

        self.SESSION.Conf.settings_["PROGRAM"].program_threads = threads
        self.SESSION.Conf.settings_["VERBOSITY"].verbosity = verbosity
        self.SESSION.Conf.update()
        self.intruder.run()

    def results(self):
        return self.intruder.get_results()
