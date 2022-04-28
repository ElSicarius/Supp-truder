from curses import raw
from email.mime import base
from shutil import ExecError
import requests
import time

from .printing import print, log, Colors, Strings

class Request():
    def __init__(self, url, data:str()="", headers: dict()={}, method="GET", parameter="", placeholder="§", place=["url"]):
        self.url = url
        self.data = data
        self.headers = headers
        self.method = method
        self.parameter = parameter
        self.placeholder = placeholder
        self.place = place
        self.fill_placeholders()
    
    def fill_placeholders(self,):
        if "raw" in self.place:
            if self.placeholder in self.data:
                self.place.append("data")
            if self.placeholder in "".join([k+v for k,v in self.headers.items()]):
                self.place.append("headers")
            if self.placeholder in self.url:
                self.place.append("url")
            self.place.remove("raw")
            self.place = list(set(self.place))
        if "url" in self.place:
            self.url = self.url.replace(self.placeholder, self.parameter)
        if "data" in self.place:
            self.data = self.data.replace(self.placeholder, self.parameter)
        if "headers" in self.place:
            new_headers = dict()
            for key, value in self.headers.items():
                new_headers[key.replace(self.placeholder, self.parameter)] = value.replace(self.placeholder, self.parameter)
            self.headers = new_headers

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

class Raw_Request():
    def __init__(self, raw_request, base_url=None, force_ssl=False):
        self.raw_request = raw_request
        self.raw_request_splitted = self.raw_request.splitlines()
        self.base_url = base_url
        self.protocol = "http" if not force_ssl else "https"
        self.force_ssl = force_ssl

        self.method = str()
        self.path = str()
        self.version = str()
        self.data = str()
        self.headers = {}
        self.url = str()
    
    def build_url(self):
        if self.base_url is None:
            log("No base url provided, using the host header... in http mode (change the default mode to https with the flag --force-ssl)", type="debug")
            if not "host" in self.headers.keys():
                log(f"Could not retrive URL to run the tests against :( if you don't want to precise the \"Host\" header (for example, if you are fuzzing the Host header), use the -ur flag to set an url for the target (ie \"-ur http://site.com\")",type="fatal")
                exit(1)
            self.base_url = f"{self.protocol}://{self.headers['host']}"
        else:
            if self.base_url.endswith("/"):
                self.base_url = self.base_url[:-1]
            if self.base_url.startswith("http://") and self.force_ssl:
                self.base_url= f"{self.protocol}{self.base_url[4:]}"
        self.url = f"{self.base_url}{'/' if not self.path.startswith('/') else ''}{self.path}"

    def parse_raw_request(self):
        log(f"Parsing request provided.", type="info")
        while len(self.raw_request_splitted[0]) == 0:
            self.raw_request_splitted = self.raw_request_splitted[1:]
        try:
            self.method, self.path, self.version = self.raw_request_splitted[0].split(" ")
            self.raw_request_splitted = self.raw_request_splitted[1:]
        except:
            log(f"Invalid http request ! first line {self.raw_request_splitted[0]} is invalid (not like {{method}} {{path}} {{version}}", type="fatal")
            exit(1)
        
        while len(self.raw_request_splitted) > 0 and len(self.raw_request_splitted[0]) > 0:
            try:
                k,v = self.raw_request_splitted[0].split(": ")
            except:
                log(f"Invalid header format ! {self.raw_request_splitted[0]} is invalid (not like {{key}}: {{value}}]",type="fatal")
                exit(1)
            self.headers[k.lower()] = v
            self.raw_request_splitted = self.raw_request_splitted[1:]
        
        while len(self.raw_request_splitted) > 0:
            if len(self.raw_request_splitted[0]) == 0:
                self.raw_request_splitted = self.raw_request_splitted[1:]
                continue
            if len(self.raw_request_splitted[0]) > 0:
                self.data = "\n".join(self.raw_request_splitted)
                break
    
    def __str__(self):
        return f"""{self.method}\n{self.url}\n{self.headers}\n{self.data}"""

class Requests():

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"}

    def __init__(self, method="GET", timeout=60, throttle=0.0, allow_redirects=False, verify_ssl=False, retry=False, headers={}) -> None:
        self.session = requests.Session()
        self.method = method
        self.timeout = timeout
        self.throttle = throttle
        self.allow_redirects = allow_redirects
        self.verify_ssl = verify_ssl
        self.headers.update({k.lower(): v for k,v in headers.items()})

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
        return self.request_handler(req.url, req.data, req.method, req.headers)
    
    def request_handler(self, url, data=None, method=None, headers={}):
        """
        Do a GET or a POST depending on the method set in settings (can be overrite with the method argument)
        :returns the requests.response object
        """
        method = self.method if not method else method
        if method == "GET":
            return self.get_(url, data, headers)
        if method == "POST":
            return self.post_(url, data, headers)


    def get_(self, url, data=None, headers={}):
        """
        Do a GET request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        if self.throttle > 0.0:
            time.sleep(self.throttle)

        self.headers.update({k.lower(): v for k,v in headers.items()})
        retry = True

        try:
            req = self.session.get(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                    verify=self.verify_ssl, headers=self.headers)
            if req.status_code == 429:
                log(
                    f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
        except Exception as e:
            print(f"HTTP Error: {e}")
            self.errors_count += 1
            req = None
            if self.retry and retry:
                try:
                    req = self.session.get(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                            verify=self.verify_ssl, headers=self.headers)
                    if req.status_code == 429:
                        log(
                            f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
                except:
                    self.retry_count += 1
                    req = None

                    retry = False
        return req


    def post_(self, url, data, headers={}):
        """
        Do a POST request in the session object
        check if we timeout or if we have a status 429 (rate limit reached)
        resend the request if it is set in the settings
        :returns a tuple with the request object and the parameter requested
        """
        if self.throttle > 0.0:
            time.sleep(self.throttle)

        self.headers.update({k.lower(): v for k,v in headers.items()})
        
        retry = True

        try:
            req = self.session.post(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                    verify=self.verify_ssl, headers=self.headers)
            if req.status_code == 429:
                log(
                    f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
        except Exception as e:
            print(f"HTTP Error: {e}")
            self.errors_count += 1
            req = None
            if self.retry and retry:
                try:
                    req = self.session.post(url, data=data, timeout=self.timeout, allow_redirects=self.allow_redirects,
                            verify=self.verify_ssl, headers=self.headers)
                    if req.status_code == 429:
                        log(
                            f"Rate limit reached, increase --throttle! Current is {self.throttle}", type="warning")
                except:
                    self.retry_count += 1
                    req = None

                    retry = False
        return req
