

import argparse
from curses import raw
from distutils.log import error
from email.mime import base 
import os
import re
import requests
from datetime import datetime
import random 
import signal
import sys

from loguru import logger

from .printing import print, log, Strings
from .http import Requests, Request, Empty_response, Raw_Request
from .intruder import Intruder

class Arguments():

    def get_arguments(self):
        """
        Get arguments from command line.
        """
        parser = argparse.ArgumentParser(description='~~~~~~~~~~ WASSUP Website ?? ~~~~~~~~~~')
        # Fuzzing stuff
        parser.add_argument('-u', "--url", help='Url to test',)
        parser.add_argument('-r', "--raw-request", help='Raw request prepared with the placeholder',)
        parser.add_argument("-d", "--data", default=None, help="Add POST data")
        parser.add_argument("-H", "--headers", default=None, action="append", help="Add extra Headers (syntax: -H \"test: test\" -H \"test2: test3\")")
        parser.add_argument("-S", "--placeholder", default="§")
        parser.add_argument("--force-ssl", default=False, help="Force https when using raw-request", action="store_true")
        parser.add_argument("-ur", "--url-raw", default=None, help="Force usage of a specific URL to make the raw request. Default: Using the Host header")
        parser.add_argument("--fuzz-recursive", action="store_true", default=False, help="Fuzz recursively by appending positive results to 'prefix' or 'suffix' and starting over (useful when doing timebased things/boolean based things)")
        parser.add_argument("--fuzz-recursive-position", default="prefix", choices=["prefix","suffix"], help="Select the position where the matching payload will be appended")
        parser.add_argument("--fuzz-recursive-separator", default="", help="Set a character/string beteen positive recursive matches")



        # tool settings
        parser.add_argument("--shuffle", help="Shuffle the payload list", default=False, action="store_true")
        parser.add_argument('-v', '--verbosity', action='count', default=1, help='verbosity level (3 levels available)')
        parser.add_argument('-t', '--threads', type=int, default=10, help='number of threads to use, default 10')
        parser.add_argument("--throttle", help="throttle between the requests, default 0.0", default=0, type=int)
        parser.add_argument('-re', "--allow-redirects", default=False, action="store_true", help='Allow HTTP redirects')
        parser.add_argument('-P', "--distant-payload", default=None, help="use an online wordlist instead of a local one (do not use if your internet connection is shit, or the wordlist weight is like To)")
        parser.add_argument("-R", "--regex-payload", help="use a regex to create your payload list", default=None)
        parser.add_argument('-p', "--payload", help='payload file',default=None)
        parser.add_argument("--prefix", help='Prefix for all elements of the wordlist',default=str())
        parser.add_argument("--suffix", help='Suffix for all elements of the wordlist',default=str())
        parser.add_argument("--offset", help='Offset to start from in the wordlist',default=0, type=int)
        parser.add_argument("--timeout", default=20, type=int)
        parser.add_argument("--retry", default=False, action="store_true")
        parser.add_argument("--verify-ssl", default=False, action="store_true")
        parser.add_argument("-X", "--method", default="GET", help="HTTP method to use")
        parser.add_argument("-f", "--filter", help="Filter positives match with httpcode,to exclude one, prefix \"n\", examples: -f n204 -f n403", action="append", default=[])
        parser.add_argument("-T", "--tamper",help="Use tamper scripts located in the tamper directory (you can make your own), ou can also chain them (processed in the order)", default=[], action="append")
        parser.add_argument("-ut", "--untamper",help="Unprocess tampered payload to see what is the real payload unprocessed", default=False, action="store_true")
        parser.add_argument("-tf", "--time-filter",help='Specify the time range that we\'ll use to accept responses (format: >3000 or <3000 or =3000 or >=3000 or <=3000', action="append", default=[])
 
        parser.add_argument("-lf", "--length-filter",help='Specify the length range that we\'ll use to accept responses (format: >3000 or <3000 or =3000 or >=3000 or <=3000', action="append", default=[])
        
        # base request stuff
        parser.add_argument("-B", "--use-base-request", help="Use the strategy to compare responses agains a base request to reduce noise",action="store_true", default=False)
        parser.add_argument('-b', "--base-payload",help="Payload for base request", default="Fuzzing")
        parser.add_argument("--ignore-base-request", default=False, action="store_true", help="Force testing even if base request failed")
        parser.add_argument("-timed", "--time-difference", default=2, type=int, help="Define a time difference where base_request will not be equal to the current_request, ie base request took 1 second and current took 2 seconds, they are different until time_different>=1")
        parser.add_argument("-textd", "--text-difference-ratio", default=0.98, type=float, help="Define a text difference where base_request.text will not be equal to the current_request.text, ie base_request matches current_request at 98%%, they are different until time_different>=0.98")
        parser.add_argument("--ratio-type", default="quick", help="Use a quick ratio of a normal one, quick is faster, normal is for very short pages")
        parser.add_argument("-m", '--match-base-request',action="store_true", default=False, help="Match the base request to find pages identical to your base payload")
        parser.add_argument('-mh', "--match-headers",help="Extends the match algorithm to the headers", default=False, action="store_true")
        parser.add_argument('-eh', "--exclude-headers",help="Exclude a header while extending the match algorithm to the headers", default=[], action="append")


        # parser.add_argument('-o', '--dumpHtml', help='file to dump html content')
        # parser.add_argument("-q", "--quiet", help="tell the program to output only the results",
        #                     default=False, action="store_true")
        self.args = parser.parse_args()
        return self.validate_arguments()

    def validate_arguments(self,):
        """
        Validate arguments.
        """
        if self.args.url is None and self.args.raw_request is None:
            log("[!] You must specify a url to test (-u) or a request file (-r) !", type="fatal")
            exit(1)

        if self.args.payload is None and self.args.regex_payload is None and self.args.distant_payload is None:
            log("[!] You must specify a payload file (-p) or a regex (-R) or a distant payload (-P) !", type="fatal")
            exit(1)
        self.tampers = None
        if len(self.args.tamper) > 0:
            self.tampers = []
            for tamper in self.args.tamper:
                loaded = self.load_tamper(tamper)
                self.tampers.append(loaded)
                self.check_tamper(loaded)
            
        if self.args.raw_request is not None:
            try:
                with open(self.args.raw_request) as f:
                    self.args.raw_request = f.read()
            except Exception as e:
                log(f"Failed to open the raw request file !", type="critical")
                exit(1)
        
        if len(
            set(filter(None, [
                self.args.url,
                self.args.raw_request
            ])
            )
        ) > 1:
            log("You've specified more that one method to make requests, that's dump :/ -u OR -r!", type="critical")
            exit(1)
        
        if len(
            set(filter(None, [
                self.args.regex_payload,
                self.args.distant_payload,
                self.args.payload
            ])
            )
        ) > 1:
            log("You've specified more that one method to define payloads, that's dump :/ -p OR -R OR -P!", type="critical")
            exit(1)
    
        self.load_headers()
        return self.args
    
    def find_place(self):
        """
        Find the place where to put the payload.
        """
        self.place = list()
        if self.args.data is not None and self.args.placeholder in self.args.data:
            self.place.append("data")
        if self.args.url is not None and self.args.placeholder in self.args.url or\
             self.args.url_raw is not None and self.args.placeholder in self.args.url_raw:
            self.place.append("url")
        if self.args.placeholder in "".join([k+v for k,v in self.args.headers.items()]):
            self.place.append("headers")
        if self.args.raw_request is not None and self.args.placeholder in self.args.raw_request:
            # defined later when parsing
            self.place.append("raw")
        
        if len(self.place) == 0:
            log(f"You mush specify the placeholder \"{self.args.placeholder}\" where you're trying to fuzz !", type="critical")
            exit(1)
 
    def load_tamper(self, module):
        module_path = f"tampers.{module}"

        if module_path in sys.modules:
            return sys.modules[module_path]
        try:
            load = __import__(module_path, fromlist=[module])
        except ModuleNotFoundError:
            log(f"Could not find the module \"{module}\" !", type="fatal")
            log(f"Here is the list of available modules: {', '.join([x[:-3] for x in os.listdir('tampers/') if x.endswith('.py')])}", type="debug")
            exit(1)
        except Exception as e:
            log(f"Failed to load the module {module}, please make sure you've put it in the tampers directory", type="critical")
            log(f"Here is your stacktrace: {e}", type="debug")
            exit(1)
        else:
            return load
    
    def load_headers(self,):
        """
        Load headers from the file.
        """
        headers_temp = dict()
        if self.args.headers is not None:
            for header in self.args.headers:
                if ":" in header:
                    key, value = header.split(": ")
                    headers_temp[key] = value
                else:
                    headers_temp[header] = str()
        self.args.headers = headers_temp
    
    def check_tamper(self, tamper):
        try:
            dummyCheck = tamper.process("Th1s Is @ Nice DummyCheck …")
            log(f"[*] Dummy check for the tamper module loaded: \"Th1s Is @ Nice DummyCheck …\" -> \"{dummyCheck}\"", type="debug")
            if isinstance(dummyCheck, bytes):
                log(f"Your tamper script should only return string and not bytes ! can't continue...", type="error")
                exit(1)
        except Exception as e:
            log(f"An exception occured in your tamper script !", type="critical")
            log(f"Hint: Can you find the 'process' function in your tamper script ?\n Stack trace: {e}", type="debug")
            exit(1)

class Wordlist():
    def __init__(self, 
                    mode, 
                    link=None, 
                    tampers=None, 
                    shuffle=False, 
                    offset=0, 
                    prefix="", 
                    suffix="",
                    fallback=None):
        self.mode = mode
        self.link = link
        self.tampers = tampers
        self.shuffle = shuffle
        self.offset = offset
        self.prefix = prefix
        self.suffix = suffix
        self.payload_list = list()
    
    def gen_wordlist_iterator(self, recursive_prefix=[], recursive_suffix=[], recursive_separator=""):
        for payload in self.payload_list:
            yield payload, f"{self.prefix}{recursive_separator.join(recursive_prefix)}{recursive_separator}{payload}{recursive_separator}{recursive_separator.join(recursive_suffix)}{self.suffix}"
    
    def get_distant_payload(self):
        try:
            log(f"Fetching wordlist ... ", type="info")
            content = requests.get(self.link).text
            self.payload_list = content.splitlines()[self.offset:]
        except Exception as e:
            log(f"Could not find the distant payload: {e}", type="fatal")
            exit(1)
    
    def get_local_payload(self):
        if not os.path.exists(self.link):
                log("[!] Payload file doesn't exist", type="fatal")
                exit(1)
        with open(self.link, "r") as f:
            self.payload_list = f.read().splitlines()[self.offset:]
        
    def apply_tamper(self):
        modified_payload_list = list()
        for payload in self.payload_list:
            tempo = payload
            for tamper in self.tampers:
                try:
                    tempo = tamper.process(tempo)
                    if isinstance(tempo, bytes):
                        log(f"Your tamper script should only return string and not bytes ! can't continue...", type="critical")
                        log(f"It translates {payload} to -> {tempo}", type="debug")
                        exit(1)
                except Exception as e:
                    log(f"An exception occured in your tamper script ! Below is the stack trace of your script.", type="critical")
                    log(f"Error: {e}", type="debug")
                    exit(1)
            modified_payload_list.append((payload, tempo))

        self.payload_list = [x[1] for x in modified_payload_list]
        self.old_payload_list = modified_payload_list
    
    def unapply_tamper(self, payload):
        tempo = payload
        for tamper in self.tampers[::-1]:
            try:
                if not "unprocess" in dir(tamper):
                    log(f"To use untamper functionnality, you need a function 'unprocess' in your tamper script !", type="fatal")
                    exit(1)
                tempo = tamper.unprocess(tempo)
                if isinstance(tempo, bytes):
                    log(f"Your tamper script should only return string and not bytes ! can't continue...", type="critical")
                    log(f"It translates {payload} to -> {tempo}", type="debug")
                    exit(1)
                
            except Exception as e:
                log(f"An exception occured in your tamper script ! Below is the stack trace of your script.", type="critical")
                log(f"Error: {e}", type="debug")
                exit(1)
        return tempo
    
    def shuffle_payloads(self):
        log("[*] Shuffling payloads", type="info")
        self.payload_list = self.payload_list
        random.Random(1337).shuffle(self.payload_list)
    
    def gen_regex_payload(self):
        try:
            import exrex
        except:
            log(f'Missing dependency "exrex"! if you want to use the regex payload generation, you have to use this command first: "pip3 install exrex"', type="fatal")
            exit(1)
        try:
            re.compile(self.link)
        except:
            log(f"Bad regex !! please check that your regex is correct !", type="fatal")
            exit(1)
        log(f"[*] Generating the payload list based on your regex", type="info")

        self.payload_list = list(exrex.generate(self.link))[self.offset:]

    def load_wordlist(self):
        if self.mode == "local_payload":
            self.get_local_payload()
        
        elif self.mode == "distant_payload":
            self.get_distant_payload()
        
        elif self.mode == "regex_payload":
            self.gen_regex_payload()
        
        if self.shuffle:
            self.shuffle_payloads()
        
        if self.tampers and len(self.tampers) > 0:
            self.apply_tamper()
        
        self.max_len_payload = len(max(self.payload_list, key=len))

class Fuzzer():

    def __init__(self, args):
        self.arguments_object = args
        self.args = self.arguments_object.get_arguments()
        self.arguments_object.find_place()
        self.start_date = datetime.now()
        self.load_request()
    
    def load_request(self,):
        if self.args.url is not None:
            self.requests = Requests(
                    method=self.args.method, 
                    timeout=self.args.timeout, 
                    throttle=self.args.throttle, 
                    allow_redirects=self.args.allow_redirects, 
                    verify_ssl=self.args.verify_ssl, 
                    retry=self.args.retry,
                    headers=self.args.headers)
        elif self.args.raw_request is not None:
            
            raw_request_parsed = Raw_Request(self.args.raw_request, self.args.url_raw, self.args.force_ssl)
            raw_request_parsed.parse_raw_request()
            raw_request_parsed.build_url()
            method, url, headers, data = \
                 raw_request_parsed.method, raw_request_parsed.url, raw_request_parsed.headers, raw_request_parsed.data
            
            self.args.method = method
            self.args.url = url
            self.args.headers.update(headers)
            self.args.data = data if not self.args.data else self.args.data

            self.requests = Requests(
                    method=self.args.method, 
                    timeout=self.args.timeout, 
                    throttle=self.args.throttle, 
                    allow_redirects=self.args.allow_redirects, 
                    verify_ssl=self.args.verify_ssl, 
                    retry=self.args.retry,
                    headers={k: v for k,v in self.args.headers.items() if not self.args.placeholder in v and not self.args.placeholder in k})

    def gen_wordlist(self):
        if self.args.payload is not None:
            mode = "local_payload"
            link = self.args.payload
        elif self.args.distant_payload is not None:
            mode = "distant_payload"
            link = self.args.distant_payload
        elif self.args.regex_payload is not None:
            mode = "regex_payload"
            link = self.args.regex_payload
        else:
            mode = None
            link = None

        self.wordlist = Wordlist(mode=mode, 
                                link=link, 
                                tampers=self.arguments_object.tampers, 
                                shuffle=self.args.shuffle, 
                                offset=self.args.offset, 
                                prefix=self.args.prefix, 
                                suffix=self.args.suffix)
        self.wordlist.load_wordlist()
        self.print(1, Strings.wordlist_loaded.format(payload_len=len(self.wordlist.payload_list)), color="green")

    def prepare(self):
        self.print(1, Strings.banner, color="yellow")
        self.gen_wordlist()
        self.intruder = Intruder(self.args, self.arguments_object.place, self.wordlist)
        if self.args.use_base_request:
            log(f"[+] Requesting base request", type="info")
            self.intruder.do_base_request()
            if self.intruder.base_request is None:
                log(f"Base request failed !", type="critical")
                if not self.args.ignore_base_request:
                    log(f"To ignore this and continue, append flag --ignore-base-request", type="debug")
                    exit(1)  
                log(f"Ignoring base request failed (the base request is not useless)", type="warning")
                self.intruder.base_request = Empty_response()
            if len(self.intruder.base_request.text) > 100:
                base_request_text_top = self.intruder.base_request.text[:50]
                base_request_text_bottom = self.intruder.base_request.text[-50:]
            else:
                base_request_text_top = self.intruder.base_request.text
                base_request_text_bottom = ""


            self.print(1, Strings.base_request_details.format(
                status=self.intruder.base_request.status_code,
                content_len=len(self.intruder.base_request.text),
                total_seconds=self.intruder.base_request.elapsed.total_seconds(),
                text_top=base_request_text_top,
                text_bottom=base_request_text_bottom),
                color=self.intruder.requests.color_status_code(self.intruder.base_request)
            )
    
    def run(self):
        @staticmethod
        def signal_handler(sig, frame):
            log(f"Caught ctrl+c, stopping...", type="warning")            
            exit(1)
        signal.signal(signal.SIGINT, signal_handler)

        self.print(1, Strings.results_header, color="white")
        responses = self.intruder.start_requests()
        for status, response, parameter, full_payload in responses:
            parameter_print = full_payload
            if self.args.untamper:
                parameter_print = self.wordlist.unapply_tamper(parameter)
            if status:
                if response is None:
                    response = Empty_response()
                self.print(1, Strings.results.format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    payload_index=f"{self.wordlist.payload_list.index(parameter)}",
                    payload_len=len(self.wordlist.payload_list),
                    status=response.status_code,
                    length=len(response.text),
                    response_time=f"{response.elapsed.total_seconds():.6f}",
                    payload=parameter_print),
                        color=self.intruder.requests.color_status_code(response))
                continue
            self.print(1, Strings.results.format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    payload_index=f"{self.wordlist.payload_list.index(parameter)}",
                    payload_len=len(self.wordlist.payload_list),
                    status=response.status_code,
                    length=len(response.text),
                    response_time=f"{response.elapsed.total_seconds():.6f}",
                    payload=parameter_print),
                        color=self.intruder.requests.color_status_code(response), end=f"{' '*os.get_terminal_size()[1]}\r")
    
    def print(self, verbosity=0, *args, **kwargs):
        if self.args.verbosity <= verbosity:
            print(*args, **kwargs)

def main():
    args = Arguments()
    fuzzer = Fuzzer(args)
    fuzzer.prepare()
    fuzzer.run()

    