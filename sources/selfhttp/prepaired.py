

from .utils import  color_status
from sources.utils import random_gen
from sources.settings.COLORS import *
from time import sleep
import sources.selfhttp as selfhttp
import re

from urllib.parse import urlparse

class PrepairedRequest(selfhttp.Request):

    def __init__(self, session):
        # init super -> Request object
        super().__init__(session)
        self.SESSION = session

    def request_maker_with_args(self, url, method="GET",data=None, headers={}):
        """
        takes target with argument list and returns the request made with the method defined, + it returns
        the formatted arguments (to keep the random strings generated for each params)
        """
        # send the parameters to the right handler with the params nicely formatted

        if method == 'GET':
            return self.request_handler(url, method=method, headers=headers)
        else:
            return self.request_handler(url, method=method, data=formatted_params, headers=headers)


    def request_handler(self, url, method, data=None, headers=None):
        """
        Do a GET or a POST depending on the method set in settings (can be overriden with the method argument)
        :returns the requests.response object
        """
        # for each requested method, do the good request formated with the rights headers
        if method == "GET":
            return self.get_(url, headers=headers)

        if method == "POST":
            if not headers:
                headers = self.SESSION.Conf.settings_["REQUEST"].request_post_headers_form
            else:
                headers.update(self.SESSION.Conf.settings_["REQUEST"].request_post_headers_form)
            return self.post_(url, data, headers=headers)

        ### # TODO: rework the next cases
        if method == "JSON":
            if not headers:
                headers = self.SESSION.Conf.settings_["REQUEST"].request_post_headers_json
            else:
                headers.update(self.SESSION.Conf.settings_["REQUEST"].request_post_headers_json)
            return self.post_(url, data, headers=headers)
        if method == "XML":
            if not headers:
                headers = self.SESSION.Conf.settings_["REQUEST"].request_post_headers_xml
            else:
                headers.update(self.SESSION.Conf.settings_["REQUEST"].request_post_headers_xml)
            return self.post_(url, data, headers=headers)

    def get_base_request(self, url, method="GET", data=None, headers=None):
        """
        Generate a first request to the target with a dummy payload to determine the origin status, length and content

        this will set the settings request object to the request made
        """
        # initial request
        req = self.request_maker_with_args(
            url, method=method, data=data, headers=headers)
        # find if the request is satisfying
        if not req:
            self.SESSION.printcust(f"{color_red}[ERROR] Error requesting base request !")
            self.SESSION.printcust(
                f"{color_red}[ERROR] We can't test this target, Stopping here...{color_end}")
        else:
            self.SESSION.printcust(f"""{color_green}[INFO] Base request info:
        {color_light_blue}[DEBUG] Method used: {color_end}{method},
        {color_light_blue}[DEBUG] status: {color_status(req.status_code)}{color_end},
        {color_light_blue}[DEBUG] content-length: {color_end}{len(req.text)},
        {color_light_blue}[DEBUG] Response time: {color_end}{req.elapsed.total_seconds()}{color_end}""", v=2)
            self.SESSION.printcust(
                f"""        {color_light_blue}[DEBUG] Request text (trucated) was: {color_banner}{req.text if len(req.text)<=100 else req.text[:50]+f" {color_yellow}[...] "+req.text[-50:]}\n{color_end}""", v=3)
        return req
