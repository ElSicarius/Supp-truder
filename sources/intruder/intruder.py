
from sources.selfhttp import PrepairedRequest, Target
from sources.selfhttp import color_status, color_triggers
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, CancelledError, thread
from sources.settings.COLORS import *

class Intruder(PrepairedRequest):
    def __init__(self, session):
        super().__init__(session)
        self.SESSION = session
        self.results = dict()
        self.TARGETS = set()

    def _self_update(self):
        self.METHOD = self.SESSION.get_method()
        self.DATA = self.SESSION.get_data()
        self.HEADERS = self.SESSION.get_headers()
        self.TARGETS = self.SESSION.get_targets()
        self.TAMPER = self.SESSION.get_tamper()
        self.THREADS = self.SESSION.get_threadscount()
        self.IGNORE_BASE_REQUEST, self.MACH_BASE_REQUEST = self.SESSION.base_req_match()

    def threading(self, target, pack_, triggers, base_request):
        res = dict()
        for item_n in range(len(pack_)):
            item = list(pack_)[item_n]
            current_target = target.duplicate().replace_locate(item)
            current_request = self.request_maker_with_args(
                                    current_target.URL,
                                    method=current_target.METHOD,
                                    data=current_target.DATA,
                                    headers=current_target.HEADERS
                                )
            triggers_comply = current_request.comply(triggers)
            if not self.IGNORE_BASE_REQUEST:
                request_compare = current_request.compare_requests(base_request)
                # inverse match
                if self.MACH_BASE_REQUEST:
                    request_compare = not request_compare
            else:
                request_compare = True

            #print("Triggers:",triggers_comply,"diff Request:",request_compare)
            print("\033[KItem: %s/%s Payload: %s " % (item_n,len(pack_),item), end="\r")

            if not request_compare and triggers_comply:

                res.update(
                {item_n:{
                'url': item,
                "status": current_request.status_code,
                "time":   current_request.elapsed.total_seconds(),
                "state": current_request.bool_status
                }}
                )
                time_color, length_color, diff_color = \
                color_triggers(triggers_comply, [current_request.elapsed.total_seconds(), len(current_request.text), request_compare])
                print("[+] Status %s; Time %s; Length %s; difference %s; Payload: %s" %\
                (color_status(current_request.status_code),time_color, length_color, diff_color, item))
        return res

    def run(self):
        self._self_update()
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Loading the wordlist")
        self.PAYLOADS = self.SESSION.prepare_payloads()
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Generating payloads packs with threads count")
        length_range = int(len(list(self.PAYLOADS))/self.THREADS)
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Packs length: ~{color_yellow}{length_range}{color_dark_blue} for {color_yellow}{self.THREADS}{color_dark_blue} threads.")
        payloads_packs = [set(list(self.PAYLOADS)[x:x+length_range]) for x in range(0, len(list(self.PAYLOADS)), length_range)]
        self.TRIGGERS = self.SESSION.gen_triggers()
        self.SESSION.printcust(f"{color_dark_blue}[INFO] Successfully loaded the wordlist with {color_yellow}{len(self.PAYLOADS)}{color_dark_blue} elements.")


        for target in self.TARGETS:
            target = Target(target, self.DATA, self.HEADERS, method=self.METHOD,\
             replaceStr=self.SESSION.Conf.settings_["PROGRAM"].program_replace_string)
            base_request_target = target.duplicate().replace_locate(self.SESSION.Conf.settings_["PROGRAM"].program_base_payload)
            base_request = self.get_base_request(base_request_target.URL, \
                            method=self.METHOD, data=base_request_target.DATA, \
                            headers=base_request_target.HEADERS)
            # threading
            futures = set()
            executor = ThreadPoolExecutor(max_workers=self.THREADS)

            futures.update( { executor.submit(
                    self.threading,
                    target.duplicate(),
                    pack,
                    self.TRIGGERS,
                    base_request
                    )
                for pack in payloads_packs
            } )

            while futures:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                for fut in done:
                    try:
                        r = fut.result()
                    except Exception as e:
                        self.SESSION.printcust(
                            f"{color_red}An Unhandled error occured in thread: {e}{color_end}")
                        continue
                    if r!=None:
                        for resnumber in r:
                            print(r[resnumber])









    def get_results(self):
        return self.results
