
from sources.utils import get_parser
import sources.settings as settings
from sources.utils import log_this
import sys


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

    def get_method(self):
        return self.Conf.settings_["REQUEST"].request_method

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

    def get_extra_data(self):
        return self.Conf.settings_["PROGRAM"].program_raw_data

    def get_current_method(self):
        return self.Conf.settings_["REQUEST"].request_methods
