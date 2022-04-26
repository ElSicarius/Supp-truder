import requests
import time

from .printing import print, log, Colors, Strings

class Request():
    def __init__(self, url, data:str()="", headers: dict()={}, method="GET", parameter="", placeholder="§", place="url"):
        self.url = url
        self.data = data
        self.headers = headers
        self.method = method
        self.parameter = parameter
        self.placeholder = placeholder
        self.place = place
        self.fill_placeholders()
    
    def fill_placeholders(self,):
        match self.place:
            case ["url"]:
                self.url = self.url.replace(self.placeholder, self.parameter)
            case ["data"]:
                self.data = self.data.replace(self.placeholder, self.parameter)
            case ["headers"]:
                for key, value in self.headers.items():
                    # delete to avoid keeping the placeholder in every request
                    del self.headers[key]
                    self.headers[key.replace(self.placeholder, self.parameter)] = value.replace(self.placeholder, self.parameter)

class Empty_response():
    status_code = 000
    text = ""
    content = b""
    headers = {}
    class T():
        time = 0.0
        def total_seconds(self):
            return self.time
    elapsed = T()


class Requests():

    headers = {}

    def __init__(self, method="GET", timeout=60, throttle=0.0, allow_redirects=False, verify_ssl=False, retry=False) -> None:
        self.session = requests.Session()
        self.method = method
        self.timeout = timeout
        self.throttle = throttle
        self.allow_redirects = allow_redirects
        self.verify_ssl = verify_ssl

        self.errors_count = 0
        self.retry_count = 0
        self.retry = retry
        self.disable_warning()
    
    @staticmethod
    def color_status_code(request):
        status = request.status_code
        status_string = str(status)
        if status_string.startswith("2"):
            return "green"
        if status_string.startswith("3"):
            return "cyan"
        if status_string.startswith("4"):
            return "yellow"
        if status_string.startswith("5"):
            return "red"
        return "white"
    
    @staticmethod
    def disable_warning():
        import urllib3
        urllib3.disable_warnings()
    
    def request_object_handler(self, req):
        return self.request_handler(req.url, req.parameter, req.data, req.method, req.headers)
    
    def request_handler(self, url, payload, data=None, method=None, headers={}):
        """
        Do a GET or a POST depending on the method set in settings (can be overrite with the method argument)
        :returns the requests.response object
        """
        method = self.method if not method else method
        if method == "GET":
            return self.get_(url, payload, headers)
        if method == "POST":
            return self.post_(url, data, payload, headers)


    def get_(self, url, parameter, headers={}):
        """
        Do a GET request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        if self.throttle > 0.0:
            time.sleep(self.throttle)

        temp_headers = self.headers.update(headers)

        retry = True

        try:
            req = self.session.get(url, timeout=self.timeout, allow_redirects=self.allow_redirects,
                    verify=self.verify_ssl, headers=temp_headers)
            if req.status_code == 429:
                log(
                    f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
        except:
            self.errors_count += 1
            req = None
            if self.retry and retry:
                try:
                    req = self.session.get(url, timeout=self.timeout, allow_redirects=self.allow_redirects,
                            verify=self.verify_ssl, headers=temp_headers)
                    if req.status_code == 429:
                        log(
                            f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
                except:
                    self.retry_count += 1
                    req = None

                    retry = False
        return (req, parameter)


    def post_(self, url, data, parameter, headers={}):
        """
        Do a POST request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        if self.throttle > 0.0:
            time.sleep(self.throttle)

        temp_headers = self.headers.update(headers)

        retry = True

        try:
            req = self.session.post(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                    verify=self.verify_ssl, headers=temp_headers)
            if req.status_code == 429:
                log(
                    f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
        except:
            self.errors_count += 1
            req = None
            if self.retry and retry:
                try:
                    req = self.session.post(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                            verify=self.verify_ssl, headers=temp_headers)
                    if req.status_code == 429:
                        log(
                            f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
                except:
                    self.retry_count += 1
                    req = None

                    retry = False
        return (req, parameter)
