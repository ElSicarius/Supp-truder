
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, CancelledError, thread
from .http import Requests, Request
from .printing import log
from .differs import Differs

class Intruder():
    def __init__(self, args, place, wordlist_generator):
        self.args = args
        self.place = place
        self.wordlist_generator = wordlist_generator
        self.requests = Requests( method=args.method, 
                                timeout=args.timeout, 
                                throttle=args.throttle, 
                                allow_redirects=args.allow_redirects, 
                                verify_ssl=args.verify_ssl, 
                                retry=args.retry)
        self.futures = set()
        self.fill_statuscode_specs()
        self.fill_time_spent_specs()
        self.fill_text_length_specs()
    
    def fill_statuscode_specs(self):
        self.status_code_specs = {"allow":set(), "deny":set()}

        def gen_statuses(base):
            if len(base) < 3:
                end = f"{str(int(base[0], 10) +1):0<3}"
            else:
                end = str(int(base)+1)

            base = f"{base:0<3}"
            return {int(x) for x in range(int(base, 10), int(end, 10))}
        
        if len(self.args.filter) == 0 :
                self.status_code_specs["allow"] = {"any"}
                return
        for spec in self.args.filter:
            if spec[0] == "n":
                self.status_code_specs["deny"] = self.status_code_specs["deny"].union(gen_statuses(spec.strip("nx")))
            else:
                self.status_code_specs["allow"] = self.status_code_specs["allow"].union(gen_statuses(spec.strip("x")))
        
        if len(self.status_code_specs["allow"]) == 0:
            self.status_code_specs["allow"].add("any")
            
    def fill_time_spent_specs(self):
        self.time_spent_specs = {"above": set(), "lower": set(), "equals": set()}
        for spec in self.args.time_filter:
            if spec.startswith(">"):
                if spec[1] == "=":
                    self.time_spent_specs["equals"].add(float(spec.strip(">=<")))
                self.time_spent_specs["above"].add(float(spec.strip(">=<")))
                continue
            if spec.startswith("<"):
                if spec[1] == "=":
                    self.time_spent_specs["equals"].add(float(spec.strip("<=>")))
                self.time_spent_specs["lower"].add(float(spec.strip("<=>")))
                continue
            if spec.startswith("="):
                self.time_spent_specs["equals"].add(float(spec.strip("=><")))
                continue
            log(f"Error while parsing time filter, unknown operand '{spec[0]}'", type="critical")
    
    def fill_text_length_specs(self):
        self.text_length_specs = {"above": set(), "lower": set(), "equals": set()}
        for spec in self.args.length_filter:
            if spec.startswith(">"):
                if spec[1] == "=":
                    self.text_length_specs["equals"].add(float(spec.strip(">=<")))
                self.text_length_specs["above"].add(float(spec.strip(">=<")))
                continue
            if spec.startswith("<"):
                if spec[1] == "=":
                    self.text_length_specs["equals"].add(float(spec.strip("<=>")))
                self.text_length_specs["lower"].add(float(spec.strip("<=>")))
                continue
            if spec.startswith("="):
                self.text_length_specs["equals"].add(float(spec.strip("=><")))
                continue
            log(f"Error while parsing length filter, unknown operand '{spec[0]}'", type="critical")

    def is_status_code_in_specs(self, status_code):
        if status_code not in self.status_code_specs["deny"] and \
            (status_code in self.status_code_specs["allow"] or "any" in self.status_code_specs["allow"]):
            return True
        return False

    def is_response_time_in_specs(self, time_elapsed):
        if len(self.time_spent_specs['equals']) == 0 and \
            len(self.time_spent_specs["above"]) == 0 and \
                len(self.time_spent_specs["lower"]) == 0:
                return True
        for equals in self.time_spent_specs["equals"]:
            if time_elapsed == equals:
                return True
        for lower in self.time_spent_specs["lower"]:
            if time_elapsed < lower:
                return True
        for above in self.time_spent_specs["above"]:
            if time_elapsed > above:
                return True
        return False

    def is_response_len_specs(self, response_len):
        if len(self.text_length_specs['equals']) == 0 and \
            len(self.text_length_specs["above"]) == 0 and \
                len(self.text_length_specs["lower"]) == 0:
                return True
        for equals in self.text_length_specs["equals"]:
            if response_len == equals:
                return True
        for lower in self.text_length_specs["lower"]:
            if response_len < lower:
                return True
        for above in self.text_length_specs["above"]:
            if response_len > above:
                return True
        return False

    def prepare_request_and_send(self, parameter):
        req = Request(self.args.url, self.args.data, self.args.headers, self.args.method, parameter, self.args.placeholder, self.place)
        return self.do_request(req)
    
    def do_base_request(self):
        dummy_parameter = self.args.base_payload
        req = Request(self.args.url, self.args.data, self.args.headers, self.args.method, self.args.base_payload, self.args.placeholder, self.place)
        self.base_request = self.do_request(req)[0]
        self.difflib = Differs(self.args.base_payload, self.args.time_difference, self.args.text_difference_ratio, self.args.ratio_type)
        return self.base_request

    def do_request(self, req):
        return self.requests.request_object_handler(req)

    def start_requests(self):
        executor = ThreadPoolExecutor(max_workers=self.args.threads)
        self.futures.update({executor.submit(self.prepare_request_and_send, p) for p in self.wordlist_generator})
        while self.futures:
            done, self.futures = wait(self.futures, return_when=FIRST_COMPLETED)
            for futu in done:
                response, parameter = futu.result()
                if response is None:
                    log(f"A problem occured while fetching the link, your internet might be broken. param: {parameter}", type="critical")
                    # Accept response
                    yield True, response, parameter
                    continue
                
                # Base request checks
                if self.args.use_base_request:
                    if self.base_request is not None:
                        identical = self.difflib.is_identical(self.base_request, response, parameter)
                        if identical:
                            if not self.args.match_base_request:
                                yield False, response, parameter
                                continue
                        else:
                            if self.args.match_base_request:
                                yield False, response, parameter
                                continue


                # FILTERS CHECKS
                if not self.is_status_code_in_specs(response.status_code):
                    # reject response
                    yield False, response, parameter
                    continue
                if not self.is_response_time_in_specs(response.elapsed.total_seconds()):
                    # reject response
                    yield False, response, parameter
                    continue
                if not self.is_response_len_specs(len(response.text)):
                    # reject response
                    yield False, response, parameter
                    continue
                # Accept response
                yield True, response, parameter