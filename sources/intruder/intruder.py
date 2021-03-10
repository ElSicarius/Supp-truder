
from sources.selfhttp.requests import Request

class Intruder(Request):
    def __init__(self, session):
        super().__init__(session)
        self.SESSION = session
        self.results = dict()

    def run(self):
        self.results.update({"url": "none"})

    def get_results(self):
        return self.results
