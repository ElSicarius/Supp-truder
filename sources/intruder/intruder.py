
from sources.selfhttp import PrepairedRequest, Target
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, CancelledError, thread
from sources.settings.COLORS import *

class Intruder(PrepairedRequest):
    def __init__(self, session):
        super().__init__(session)
        self.SESSION = session
        self.results = dict()
        self.TARGETS = set()
        self.METHOD = self.SESSION.get_method()
        self.DATA = self.SESSION.get_data()
        self.HEADERS = self.SESSION.get_headers()



    @staticmethod
    def threading():
        return

    def run(self):
        self.TARGETS = self.SESSION.get_targets()
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Loading the wordlist")
        self.PAYLOADS = self.SESSION.prepare_payloads()
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Successfully loaded the wordlist")
        for target in self.TARGETS:
            target = Target(target, self.DATA, self.HEADERS, replaceStr=self.SESSION.Conf.settings_["PROGRAM"].program_replace_string)
            base_request_target = target.replace_locate(self.SESSION.Conf.settings_["PROGRAM"].program_base_payload)
            base_request = self.get_base_request(base_request_target.URL, \
                            method=self.METHOD, data=base_request_target.DATA, \
                            headers=base_request_target.HEADERS)







    def get_results(self):
        return self.results
