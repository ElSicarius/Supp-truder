
from sources.utils import get_parser, regex_gen
from sources.utils import Triggers
import sources.settings as settings
from sources.utils import log_this
from sources.settings.COLORS import *
import sys, re


class Session(dict):
    """Session object"""

    def __init__(self):
        super().__init__()
        self.Conf = settings.Settings(self._get_parser())
        self.TARGETS = self._load_targets()

    def _get_parser(self):
        """ find parameters fom user input """
        return get_parser()

    def _load_targets(self):
        target = set()
        if self.Conf.settings_["PROGRAM"].program_target:
            target.add(self.Conf.settings_["PROGRAM"].program_target)
        else:
            target = None
        return target

    def get_targets(self):
        return self._load_targets()

    def base_req_match(self):
        return self.Conf.settings_["DIFFLIB"].difflib_ignore_base_request,\
               self.Conf.settings_["DIFFLIB"].difflib_base_request_match

    def gen_triggers(self):
        self.triggers = Triggers(self)
        return self.triggers

    def get_method(self):
        return self.Conf.settings_["REQUEST"].request_method

    def get_payloads(self):
        return self.Conf.settings_["FILES"].files_wordlist_var

    def get_mutations(self):
        return self.Conf.settings_["PROGRAM"].wordlist_mutations

    def get_tamper(self):
        return self.Conf.settings_["TAMPER"]

    def get_threadscount(self):
        return int(self.Conf.settings_["PROGRAM"].program_threads)

    def prepare_payloads(self):
        mutations = self.get_mutations()
        if not len(mutations)>0:
            return self.get_payloads()
        self.printcust(f"{color_green}\t[DEBUG] Applying {len(mutations)} mutations to the wordlist !")
        temp_payload = set()
        payloads_merged = "\n".join(self.get_payloads())
        final_payloads = set(self.get_payloads())
        for mutation in mutations:
            if re.findall(mutation[0], payloads_merged):
                for payload in self.get_payloads():
                    if re.findall(mutation[0], payload):
                        if mutation[2]:
                            try:
                                final_payloads.remove(payload)
                            except:
                                pass
                        regex_generated = regex_gen(mutation[1])
                        for regex in regex_generated:
                            final_payloads.add(re.sub(mutation[0], regex, payload))

        return final_payloads

    def get_data(self):
        return self.Conf.settings_["PROGRAM"].program_raw_data

    def get_headers(self):
        return self.Conf.settings_["REQUEST"].request_base_headers

    def printcust(self, text, end="\n", v=1, nolog=False):
        """
        Custom print function that takes an extra argument "verbosity"
        log -> file handler for logging
        """
        if 0 < self.Conf.settings_["VERBOSITY"].verbosity >= v:
            print(text, end=end)
        if not nolog:
            log_this(text, self.Conf.settings_["FILES"].files_full_log_var,\
             self.Conf.settings_["COLORS"].color_list)
