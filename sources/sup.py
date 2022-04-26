

import argparse
from email.mime import base 
import os
import re
import requests
from datetime import datetime
import random 
import sys

from loguru import logger

from .printing import print, log, Strings
from .http import Requests, Request, Empty_response
from .intruder import Intruder

class Arguments():

    def get_arguments(self):
        """
        Get arguments from command line.
        """
        parser = argparse.ArgumentParser(description='Supptruder, like SuperTruder but better')
        # Fuzzing stuff
        parser.add_argument('-u', "--url", help='Url to test',)
        parser.add_argument("-d", "--data", default=None, help="Add POST data")
        parser.add_argument("-H", "--headers", default={},
                             help="Add extra Headers (syntax: \"header: value\\nheader2: value2\")")
        parser.add_argument("-S", "--placeholder", default="§")

        # tool settings
        parser.add_argument("--shuffle", help="Shuffle the payload list", default=False, action="store_true")
        parser.add_argument('-v', '--verbosity', action='count', default=1, help='verbosity level (3 levels available)')
        parser.add_argument('-t', '--threads', type=int, default=10, help='number of threads to use, default 10')
        parser.add_argument("--throttle", help="throttle between the requests, default 0.0", default=0, type=int)
        parser.add_argument('-r', "--allow-redirects", default=False, action="store_true", help='Allow HTTP redirects')
        parser.add_argument('-P', "--distant-payload", default=None, help="use an online wordlist instead of a local one (do not use if your internet connection is shit, or the wordlist weight is like To)")
        parser.add_argument("-R", "--regex-payload", help="use a regex to create your payload list", default=None)
        parser.add_argument('-p', "--payload", help='payload file',default=None)
        parser.add_argument("--prefix", help='Prefix for all elements of the wordlist',default=str())
        parser.add_argument("--suffix", help='Suffix for all elements of the wordlist',default=str())
        parser.add_argument("--offset", help='Offset to start from in the wordlist',default=0)
        parser.add_argument("--timeout", default=20)
        parser.add_argument("--retry", default=False)
        parser.add_argument("--verify-ssl", default=False, action="store_true")
        parser.add_argument("-X", "--method", default="GET", help="HTTP method to use")
        parser.add_argument("-f", "--filter", help="Filter positives match with httpcode,to exclude one, prefix \"n\", examples: -f n204 -f n403", action="append", default=[])
        parser.add_argument("-T", "--tamper",help="Use tamper scripts located in the tamper directory (you can make your own)", default=None)
        parser.add_argument("-tf", "--time-filter",help='Specify the time range that we\'ll use to accept responses (format: >3000 or <3000 or =3000 or >=3000 or <=3000', action="append", default=[])

        parser.add_argument("-lf", "--length-filter",help='Specify the length range that we\'ll use to accept responses (format: >3000 or <3000 or =3000 or >=3000 or <=3000', action="append", default=[])
        
        # base request stuff
        parser.add_argument("-B", "--use-base-request", help="Use the strategy to compare responses agains a base request to reduce noise",action="store_true", default=False)
        parser.add_argument('-b', "--base-payload",help="Payload for base request", default="Fuzzing")
        parser.add_argument("--ignore-base-request", default=False, action="store_true", help="Force testing even if base request failed")
        parser.add_argument("-timed", "--time-difference", default=1, type=int, help="Define a time difference where base_request will not be equal to the current_request, ie base request took 1 second and current took 2 seconds, they are different until time_different>=1")
        parser.add_argument("-textd", "--text-difference-ratio", default=0.98, type=float, help="Define a text difference where base_request.text will not be equal to the current_request.text, ie base_request matches current_request at 98%, they are different until time_different>=0.98")
        parser.add_argument("--ratio-type", default="quick", help="Use a quick ratio of a normal one, quick is fatser, normal is for very short pages")
        parser.add_argument("-m", '--match-base-request',action="store_true", default=False, help="Match the base request to find pages identical to your base payload")

        # 
        # parser.add_argument('-b', "--basePayload",
        #                     help="Payload for base request", default="Fuzzing")
        # 

        # # Sorting stuff
        #
        # parser.add_argument("-m", '--matchBaseRequest',
        #                     action="store_true", default=False)
        # parser.add_argument("-el", "--excludeLength",
        #                     help='Specify the len range that we\'ll use to deny responses (eg: 0,999 or any, if 3 values, we\'ll refuse EXACTLY this values)', default="none,none")
        # parser.add_argument(
        #     "-t", "--timeFilter", help='Specify the time range that we\'ll use to accept responses (eg: 0,999 or any, if 3 values, we\'ll accept EXACTLY this values)', default="any,any")

        # # misc stuff
        # parser.add_argument('-o', '--dumpHtml', help='file to dump html content')

        # # request stuff
        # 
        # 
        # parser.add_argument(
        #     "--throttle", help="throttle between the requests", default=0.01)
        # parser.add_argument("--verify", default=False, action="store_true")

        # # program functionnalities
        # parser.add_argument(
        #     "--difftimer", help="Change the default matching timer (default 2000ms -> 2 seconds)", default=2000)
        # parser.add_argument(
        #     "--textDifference", help="Percentage difference to match pages default: 99%%", default=0.99)
        # parser.add_argument("--quickRatio", help="Force quick ratio of pages (a bit faster)",
        #                     action="store_true", default=False)
        # parser.add_argument("--threads", default=5)
        # parser.add_argument("--ignoreBaseRequest", default=False,
        #                     action="store_true", help="Force testing even if base request failed")
        # parser.add_argument("--uselessprint", help="Disable useless self-rewriting print (with '\\r')",
        #                     default=False, action="store_true")
        # parser.add_argument("-q", "--quiet", help="tell the program to output only the results",
        #                     default=False, action="store_true")
        # parser.add_argument("-v",'--verbosity', help="Change the verbosity of the program (available: 1,2,3)", default=2)
        self.args = parser.parse_args()
        return self.validate_arguments()

    def validate_arguments(self,):
        """
        Validate arguments.
        """
        if self.args.url is None:
            print("[!] You must specify a url to test")
            exit(1)
        if self.args.payload is None and self.args.regex_payload is None and self.args.distant_payload is None:
            print("[!] You must specify a payload file")
            exit(1)

        if self.args.tamper:
            self.tamper = self.args.tamper
            self.args.tamper = self.load_tamper(self.args.tamper)
            self.check_tamper()

        return self.args
    
    def find_place(self):
        """
        Find the place where to put the payload.
        """
        self.place = list()
        if self.args.data is not None and self.args.placeholder in self.args.data:
            self.place.append("data")
        elif self.args.placeholder in self.args.url:
            self.place.append("url")
        elif self.args.placeholder in self.args.headers:
            self.place.append("headers")
 
    def load_tamper(self, module):
        module_path = f"tampers.{module}"

        if module_path in sys.modules:
            return sys.modules[module_path]
        try:
            load = __import__(module_path, fromlist=[module])
        except Exception as e:
            log(f"Failed to load the module {module}, please make sure you've put it in the tampers directory", type="critical")
            log(f"Here is your stacktrace: {e}", type="debug")
            exit(1)
        else:
            return load
    
    def check_tamper(self):
        try:
            dummyCheck = self.args.tamper.process("Th1Is@NiceDummyCheck")
            log(f"[*] Dummy check for the tamper module loaded: Th1Is@NiceDummyCheck -> {dummyCheck}", type="info")
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
                        tamper=None, 
                        shuffle=False, 
                        offset=0, 
                        prefix="", 
                        suffix=""):
        self.mode = mode
        self.link = link
        self.tamper = tamper
        self.shuffle = shuffle
        self.offset = offset
        self.prefix = prefix
        self.suffix = suffix
        self.payload_list = list()
    
    def gen_wordlist_iterator(self):
        for payload in self.payload_list:
            yield f"{self.prefix}{payload}{self.suffix}"
    
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
            try:
                tempo = self.tamper.process(payload)
                if isinstance(tempo, bytes):
                    log(f"Your tamper script should only return string and not bytes ! can't continue...", type="critical")
                    log(f"It translates {payload} to -> {tempo}", type="debug")
                    exit(1)
                modified_payload_list.append((payload, tempo))
            except Exception as e:
                log(f"An exception occured in your tamper script ! Below is the stack trace of your script.", type="critical")
                log(f"Error: {e}", type="debug")
                exit(1)
        self.payload_list = [x[1] for x in modified_payload_list]
        self.old_payload_list = modified_payload_list
    
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
        
        if self.tamper:
            self.apply_tamper()
        
        self.max_len_payload = len(max(self.payload_list, key=len))

class Fuzzer():

    def __init__(self, args):
        self.arguments_object = args
        self.args = self.arguments_object.get_arguments()
        self.arguments_object.find_place()
        self.requests = Requests(method="GET", timeout=60, throttle=0.0, allow_redirects=False, verify_ssl=False, retry=False)
        self.start_date = datetime.now()

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
                                tamper=self.args.tamper, 
                                shuffle=self.args.shuffle, 
                                offset=self.args.offset, 
                                prefix=self.args.prefix, 
                                suffix=self.args.suffix)
        self.wordlist.load_wordlist()
        self.print(1, Strings.wordlist_loaded.format(payload_len=len(self.wordlist.payload_list)), color="green")

    def prepare(self):
        self.print(1, Strings.banner, color="yellow")
        self.gen_wordlist()
        self.intruder = Intruder(self.args, self.arguments_object.place, self.wordlist.gen_wordlist_iterator())
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
        self.print(1, Strings.results_header, color="white")
        responses = self.intruder.start_requests()
        for status, response, parameter in responses:
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
                    payload=parameter),
                        color=self.intruder.requests.color_status_code(response))
                continue
            self.print(1, Strings.results.format(
                    time=datetime.now().strftime("%H:%M:%S"),
                    payload_index=f"{self.wordlist.payload_list.index(parameter)}",
                    payload_len=len(self.wordlist.payload_list),
                    status=response.status_code,
                    length=len(response.text),
                    response_time=f"{response.elapsed.total_seconds():.6f}",
                    payload=parameter),
                        color=self.intruder.requests.color_status_code(response), end=f"{' '*os.get_terminal_size()[1]}\r")
    
    def print(self, verbosity=0, *args, **kwargs):
        if self.args.verbosity <= verbosity:
            print(*args, **kwargs)

def main():
    args = Arguments()
    fuzzer = Fuzzer(args)
    fuzzer.prepare()
    fuzzer.run()

    