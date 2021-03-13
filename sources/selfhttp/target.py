
import copy
class Target(dict):

    def __init__(self, url, data, headers,base_request=None, method='GET', payload_locations=None, replaceStr="§"):
        self.URL = url
        self.DATA = data
        self.HEADERS = headers
        self.LOCATIONS = payload_locations or set()
        self.REPLACESTR = replaceStr
        self.METHOD = method
        self.BASE_REQUEST = base_request
        if not self.LOCATIONS:
            self.locate_replacestr()
        print(f"Located {self.LOCATIONS}")

    def replace_locate(self, replace_with):
        for location in self.LOCATIONS:
            if location == "url":
                self.URL = self.URL.replace(self.REPLACESTR, replace_with)
            if location == "data":
                if data:
                    self.DATA = self.DATA.replace(self.REPLACESTR, replace_with)
            if location == "headers":
                for i,v in self.HEADERS.items():
                    self.HEADERS[i] = v.replace(self.REPLACESTR, replace_with)
        return self

    def duplicate(self):
        return copy.deepcopy(self)

    def locate_replacestr(self):
        if self.REPLACESTR in self.URL:
            self.LOCATIONS.add("url")
        if self.DATA and self.REPLACESTR in self.DATA:
            self.LOCATIONS.add("data")
        if self.REPLACESTR in self.HEADERS:
            self.LOCATIONS.add("headers")
