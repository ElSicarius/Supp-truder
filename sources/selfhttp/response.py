
from sources.settings.COLORS import *

class Response():
    """
    Class response designed to be the same values as a request.object from Requests lib. But smarter.
    """
    class Time():
        """
        to process time things
        """
        def __init__(self, time):
            self.time = time if time > 0 else 1

        def total_seconds(self):
            """
            Returns the time in seconds.microseconds
            """
            return self.time
    def __init__(self, content, status=0, time=0, headers=dict(), url="", bool_status=False, ua=""):
        """
        Init the response object
        """
        self.text = content
        self.headers = headers
        self.headers_formatted = self._format_headers(self.headers)
        self.status_code = status
        self.elapsed = self.Time(time)
        self.url = url
        self.ua = ua
        self.bool_status = bool_status
        self.full_content = self._merge_attributes(self)
        return
    @staticmethod
    def _format_headers(headers):
        return "\n".join([f"{name}: {value}" for name,value in headers.items()])

    @staticmethod
    def _merge_attributes(response):
        return f"{response.headers_formatted}\n\n{response.text}"
    def __str__(self):
        return f"""{color_light_blue}[XTREME][DEBUG] URL: {self.url}
        \rreq status: {self.status_code}
        \rreq time: {self.elapsed.total_seconds()}
        \rreq user-agent: {self.ua}
        \req.content: {self.text}"""

    def __bool__(self):
        """
        *I'm True or false ?*
        """
        return self.bool_status

    __nonzero__ = __bool__
