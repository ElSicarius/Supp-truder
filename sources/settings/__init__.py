
import re
import os
import sys
import importlib
import json

import sources.utils as utils
import sources.selfhttp.utils as httputils
from sources.selfhttp import Proxy

class Settings(dict):
    """
    settings object
    """

    def __init__(self, parser):
        """Default settings values"""

        super().__init__()
        self.settings_ = self._load_settings(parser)
        self.DATABASE = "./database"
        self.DOMAIN = "test"
        self._set_magic_vars()
        self._process_self()
        self.PROXY = self._prepare_proxy()

    def __setitem__(self, name, value):
        name = name.replace('-', '_').upper()
        if not self._isattr(name):
            raise KeyError("illegal name: '{}'".format(name))
        return super().__setitem__(self, name, value)

    def _update_domain(self, target):
        self.DOMAIN = target
        self._set_magic_vars()
        self.settings_ = self._process_files_options(self.settings_)

    def update(self):
        return

    def _set_magic_vars(self):
        for module in self.settings_:
            for variable in [v for v in dir(self.settings_[module]) if v[:2] != "__"]:
                value = getattr(self.settings_[module], variable)
                if "%%DOMAIN%%" in str(value):
                    value = value.replace("%%DOMAIN%%", self.DOMAIN)
                if "%%DATABASE%%" in str(value):
                    value = value.replace("%%DATABASE%%", self.DATABASE)
                # live files with content are now named with a "_var" at the end
                setattr(self.settings_[module], variable+"_var", value)


    def _prepare_proxy(self):
        return Proxy(self.settings_["REQUEST"].request_proxy)

    def _process_self(self):
        self.settings_["REQUEST"] = self._process_request_options(self.settings_["REQUEST"])
        # files processing and dispatch
        self.settings_["FILES"] = self._process_files_options(self.settings_["FILES"])
        self.settings_["COLORS"] = self._process_colors_options(self.settings_["COLORS"])
        self.settings_["PROGRAM"] = self._process_program_options(self.settings_["PROGRAM"])
        self.settings_["DIFFLIB"] = self._process_diff_options(self.settings_["DIFFLIB"])
        self.settings_["TAMPER"] = self._load_tamper(self.settings_)

    @staticmethod
    def _process_request_options(module):

        return module

    @staticmethod
    def _load_tamper(settings):
        tamper = None
        if not settings["PROGRAM"].program_tamper:
            tamper = False
        dirname = os.path.dirname(settings["FILES"].files_tampers_path)
        sys.path.insert(0, dirname)
        for file in os.listdir(dirname):
            if not re.match(r"^[A-Z][A-Z0-9_]+\.py$", file):
                continue
            name = file[:-3]
            module = importlib.import_module(name)
            tamper = module
        sys.path.pop(0)
        if tamper == None:
            raise ValueError(f"Unknown tamperscript {settings['PROGRAM'].program_tamper}")
        return tamper

    @staticmethod
    def _process_diff_options(module):
        if module.difflib_delete_html_tag:
            module.difflib_delete_html_tag = utils.load_tag_del(module.difflib_delete_html_tag)
        return module

    @staticmethod
    def _process_files_options(module):
        # logs handlers
        utils.create_dirs(module.files_full_log_var)
        utils.create_dirs(module.files_output_log_var)
        module.files_full_log_var = utils.file_opener(module.files_full_log_var, "a+")
        module.files_output_log_var = utils.file_opener(module.files_output_log_var, "a+")
        # wordlists
        module.files_wordlist_var = utils.open_and_split(module.files_wordlist_var)
        module.files_distant_wordlist = utils.open_distant_and_split(module.files_distant_wordlist)
        if not module.files_wordlist_var and module.files_distant_wordlist:
            module.files_wordlist_var = module.files_distant_wordlist
        if not module.files_wordlist_var:
            print("Error while choosing your payloads list :S")
        return module

    @staticmethod
    def _process_program_options(module):
        # nothing now

        module.program_extra_data = utils.load_raw_data(module.program_raw_data)

        return module

    @staticmethod
    def _process_colors_options(module):
        # nothing now
        # disable colors here
        return module

    @staticmethod
    def _isattr(name):
        return re.match("^[A-Z][A-Z0-9_]+$", name)

    @staticmethod
    def _load_settings(parser=None):
        settings = {}
        dirname = os.path.dirname(__file__)
        sys.path.insert(0, dirname)
        for file in os.listdir(dirname):
            if not re.match(r"^[A-Z][A-Z0-9_]+\.py$", file):
                continue
            name = file[:-3]
            module = importlib.import_module(name)
            settings[name] = module
        sys.path.pop(0)
        if parser:
            for argument_name, argument_value in vars(parser.parse_args()).items():
                if argument_value == None:
                    continue
                global_name = argument_name.split("_")[0].upper()
                setattr(settings[global_name], argument_name, argument_value)
        return settings
