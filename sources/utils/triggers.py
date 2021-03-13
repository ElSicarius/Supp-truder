

class Triggers(dict):

    def __init__(self, session):
        self.SESSION = session
        self.DIFFLIB_CONFIG = self.SESSION.Conf.settings_["DIFFLIB"]
        self.FILTERS = self.SESSION.Conf.settings_["PROGRAM"]
        self.STATUS = self.load_raw(self.FILTERS.program_status_filter)
        self.LENGTH_ALLOW = self.load_raw(self.FILTERS.program_length_filter)
        self.LENGTH_EXCLU = self.load_raw(self.FILTERS.program_length_exclusion)
        self.TIME = self.load_raw(self.FILTERS.program_time_filter)
        self._merge_length()

    def _merge_length(self):
        allow1 = self.LENGTH_ALLOW["allow"]
        deny1 = self.LENGTH_ALLOW["deny"]

        deny2 = self.LENGTH_EXCLU["allow"]
        allow2 = self.LENGTH_EXCLU["deny"]

        self.LENGTH_ALLOW["allow"] = list(set(allow1+allow2))
        self.LENGTH_EXCLU["allow"] = list(set(deny1+deny2))
    @staticmethod
    def load_raw(status_raw):
        status = dict()
        status["allow"] = list()
        status["deny"] = list()
        for stat in status_raw:
            if len(stat.split("-")) == 1 :
                if stat.startswith("n"):
                    if not stat.endswith("x"):
                        status["deny"].append([stat[1:]])
                    else:
                        for i in range(10):
                            status["deny"].append([stat[1:-1]+str(i)])
                elif stat.endswith("x"):
                    for i in range(10):
                        status["allow"].append([stat[1:-1]+str(i)])
                else:
                    status["allow"].append([stat])
                continue
            if len(stat.split("-")) == 2 :
                elements = stat.split("-")

                if elements[0] != "&":
                    elements[0] = elements[0]
                else:
                    elements[0] = "&"

                if elements[1] != "&":
                    elements[1] = elements[1]
                else:
                    elements[1] = "&"
                status["allow"].append(elements)
        return status
