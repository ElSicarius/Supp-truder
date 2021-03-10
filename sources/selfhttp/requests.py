
import urllib.request

from .utils import makeURLCompliant, get_date
from sources.settings.COLORS import *

import ssl
from ssl import _create_unverified_context
from time import sleep
import json

from .response import Response

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Request(dict):
    """
    Class defining the requests pseudo library used everywhere in the code
    """

    def __init__(self, session):
        """
        Init, keeps some settings
        """
        # disable ssl verification
        # todo noredirect modifiable
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, new_url):
                pass

        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        debugHandler = urllib.request.HTTPSHandler(context=self.context)
        self.OPENER = urllib.request.build_opener(debugHandler, session.Conf.PROXY() , NoRedirect())

        self.SESSION = session
        self.STATUS = {"time": get_date(), "req_count": 0}

    def get_(self, url, headers=None):
        """
        Do a GET request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        """
        if isinstance(self.authent, Authentification):
            if not self.authent.isConnected():
                printcust(f"{consts.yellow}[WARN][CONN] Your session has expired to the target",v=10)
                # try to refresh
                self.authent.ensureConnect()
                if not self.authent.isConnected():
                    # force reconnection
                    printcust(f"{consts.red}[ERROR][CONN] Trying the whole connection process",v=10)
                    self.authent.connect()
        """
        # make sure the url is good to go
        url = makeURLCompliant(url)
        # sleep throttle
        if self.SESSION.Conf.settings_["REQUEST"].request_throttle > 0:
            sleep(self.SESSION.Conf.settings_["REQUEST"].request_throttle)
        # merge headers to settings.headers
        temp_headers = self.SESSION.Conf.settings_["REQUEST"].request_base_headers
        # add temporary headers
        if headers:
            temp_headers.update(headers)
        # don't exceed the max request per min
        if self.SESSION.Conf.settings_["REQUEST"].request_max_req_per_min:
            time_to_sleep = self.go_time_and_request()
            if time_to_sleep > 0:
                self.SESSION.printcust(
                    f"{color_light_blue}[DEBUG] We need to sleep {abs(time_to_sleep-60)} seconds...", v=9)
                # sleep the seconds left to go to 1 minute
                sleep(abs(time_to_sleep - 60))
        try:
            # thx laluka for the tips on requests doing encoding shiet. now i'll steal your code :p
            # prepare the request
            req = urllib.request.Request(url)
            # add headers
            for key, value in temp_headers.items():
                req.add_header(key, value)
            time = 0
            # get time before the request
            now = get_date()
            try:
                # open the request
                rep = self.OPENER.open(req, timeout=self.SESSION.Conf.settings_["REQUEST"].request_timeout)
            # if there is any problem with the request (500 error is a problem for example)
            except urllib.error.HTTPError as http_err:
                rep = http_err
            # get time after
            after = get_date()
            # get time difference
            time = float((after-now).total_seconds())
            # create Response object based on what we've recieved
            req = Response(rep.read().decode('utf-8', errors='ignore'), status=rep.status,
               url=rep.url, headers=rep.headers, time=time, bool_status=True, ua=temp_headers["User-Agent"])

            # code 429 = rate limit of request
            if req.status_code == 429:
                self.SESSION.printcust('HTTP 429 - Rate limit reached')
                self.SESSION.printcust(f'Increase --throttle, current is {self.SESSION.Conf.settings_["REQUEST"].request_throttle}')
                #rate limit status
                increment_rate = 0
                # while we're on a rate limit
                while req.status_code == 429:
                    increment_rate += 1
                    self.SESSION.printcust(f'Sleeping {self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep} sec to bypass limit-rate')
                    sleep(self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep)
                    # increasing sleep delay
                    self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep += (0.2*increment_rate)
                    req = self.get_(url, temp_headers)
            if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                self.SESSION.printcust(req.__str__(), v=40, nolog=True)
            return req

        # problem in request
        except Exception as e:
            self.SESSION.printcust(f"{color_red}[ERROR] HTTP Error: {e} {url}{color_end}")
            time = float((get_date()-now).total_seconds())
            if self.SESSION.Conf.settings_["REQUEST"].request_retry:
                if self.SESSION.Conf.settings_["REQUEST"].request_throttle > 0:
                    sleep(self.SESSION.Conf.settings_["REQUEST"].request_throttle)
                try:
                    now = get_date()
                    rep = opener.open(req, timeout=self.SESSION.Conf.settings_["REQUEST"].request_timeout)

                except urllib.error.HTTPError as http_err:
                    rep = http_err
                after = get_date()
                time = float((after-now).total_seconds())
                req = Response(rep.read().decode('utf-8', errors='ignore'), status=rep.status, url=rep.url, headers=rep.headers, time=time, bool_status=True, ua=temp_headers["User-Agent"])
                if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                    printcust(req, v=40, nolog=True)
                return req
            if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                self.SESSION.printcust(req, v=40, nolog=True)
            return Response("", status=0, url=url, time=time, ua=temp_headers["User-Agent"])

    def post_(self, url, data, headers=None):
        """
        Do a POST request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        """
        if isinstance(self.authent, Authentification):
            if not self.authent.isConnected():
                printcust(f"{consts.yellow}[WARN][CONN] Your session has expired to the target",v=10)
                # try to refresh
                self.authent.ensureConnect()
                if not self.authent.isConnected():
                    # force reconnection
                    printcust(f"{consts.red}[ERROR][CONN] Trying the whole connection process",v=10)
                    self.authent.connect()
        """
        url = makeURLCompliant(url)
        if isinstance(data, dict):
            data = json.dumps(data)

        if not isinstance(data, str) and not isinstance(data, bytes):
            self.SESSION.printcust(f"{color_red}[ERROR][CODE] DATA Should be str or bytes !",v=10)
            exit(42)
        if isinstance(data, str):
            data = data.encode("utf-8")
        if self.SESSION.Conf.settings_["REQUEST"].request_throttle > 0:
            sleep(self.SESSION.Conf.settings_["REQUEST"].request_throttle)
        # get settings headers
        temp_headers = self.SESSION.Conf.settings_["REQUEST"].request_base_headers
        if headers:
            temp_headers.update(headers)
        if self.SESSION.Conf.settings_["REQUEST"].request_max_req_per_min:
            time_to_sleep = self.go_time_and_request()
            if time_to_sleep > 0:
                self.SESSION.printcust(
                    f"{color_light_blue}[DEBUG] We need to sleep {abs(time_to_sleep-60)} seconds...", v=9)
                sleep(abs(time_to_sleep - 60))
        try:
            # thx laluka for the tips on requests doing encoding shiet. now i'll steal your code :p
            req = urllib.request.Request(url)
            for key, value in temp_headers.items():
                req.add_header(key, value)
            time = 0
            try:
                now = get_date()
                rep = self.OPENER.open(req, data=data, timeout=self.SESSION.Conf.settings_["REQUEST"].request_timeout)

            except urllib.error.HTTPError as http_err:
                rep = http_err
            after = get_date()
            time = float((after-now).total_seconds())

            req = Response(rep.read().decode('utf-8', errors='ignore'), status=rep.status, url=rep.url, headers=rep.headers, time=time, bool_status=True, ua=temp_headers["User-Agent"])

            if req.status_code == 429:
                self.SESSION.printcust('HTTP 429 - Rate limit reached')
                self.SESSION.printcust(f'Increase --throttle, current is {self.SESSION.Conf.settings_["REQUEST"].request_throttle}')
            while req.status_code == 429:
                self.SESSION.printcust(f'Sleeping {self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep} sec to bypass limit-rate')
                sleep(self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep)
                # increasing sleep delay
                self.SESSION.Conf.settings_["REQUEST"].request_limit_rate_sleep += 0.2
                req = self.post_(url, data, headers=None)

            if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                self.SESSION.printcust(req, v=40, nolog=True)
            return req
        except Exception as e:
            self.SESSION.printcust(f"{color_red}[ERROR] HTTP Error: {e} url:{url} params:{data}{color_end}")
            time = float((get_date()-now).total_seconds())
            if self.SESSION.Conf.settings_["REQUEST"].request_retry:
                if self.SESSION.Conf.settings_["REQUEST"].request_throttle > 0:
                    sleep(self.SESSION.Conf.settings_["REQUEST"].request_throttle)
                try:
                    now = get_date()
                    rep = opener.open(req, data=data, timeout=self.SESSION.Conf.settings_["REQUEST"].request_timeout)

                except urllib.error.HTTPError as http_err:
                    rep = http_err
                after = get_date()
                time = float((after-now).total_seconds())
                req = Response(rep.read().decode('utf-8', errors='ignore'), status=rep.status, url=rep.url, headers=rep.headers, time=time, bool_status=True, ua=temp_headers["User-Agent"])
                if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                    self.SESSION.printcust(req, v=40, nolog=True)
                return req
            if self.SESSION.Conf.settings_["VERBOSITY"].verbosity_debug:
                self.SESSION.printcust(req, v=40, nolog=True)
            return Response("", status=0, url=url, time=time, ua=temp_headers["User-Agent"])


    def go_time_and_request(self):
        """
        Determine if we are exceding the "max requests per minute" option

        :returns the time to sleep needed
        """
        current_time = get_date()
        if (current_time - self.STATUS["time"]).seconds >= 60:
            self.STATUS["time"] = current_time
            self.STATUS["req_count"] = 0
            return 0
        else:
            if self.STATUS["req_count"] <= self.SESSION.Conf.settings_["REQUEST"].request_max_req_per_min:
                self.STATUS["req_count"] += 1
                return 0
            else:
                return (current_time - self.STATUS["time"]).seconds
