
from sources.settings.COLORS import *
from .suppdifflib import DiffLibrary as difflib
from sources.utils import is_in_range

class Response(difflib):
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
    def __init__(self, content, session=None, status=0, time=0, headers=dict(), url="", bool_status=False, ua=""):
        """
        Init the response object
        """
        super().__init__(session)
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

    def comply(self, triggers):
        allow_status, deny_status = triggers.STATUS["allow"], triggers.STATUS["deny"]
        allow_time, deny_time = triggers.TIME["allow"], triggers.TIME["deny"]
        allow_length, deny_length = triggers.LENGTH_ALLOW["allow"], triggers.LENGTH_EXCLU["allow"]
        go_status_code_pos = is_in_range((allow_status, deny_status), self.status_code)
        go_length_allow_pos = is_in_range((allow_length, deny_length), len(self.text))
        go_timer_pos = is_in_range((allow_time, deny_time), self.elapsed.total_seconds())

        #print("status",go_status_code_pos, "length", go_length_allow_pos, "timer", go_timer_pos)
        if go_status_code_pos is not None and go_status_code_pos :
            return "status"
        if go_length_allow_pos is not None and go_length_allow_pos :
            return "length_deny"
        if go_timer_pos is not None and go_timer_pos :
            return "timer"
        return False

    def compare_requests(self, second_request):
        if self.is_identical(self, second_request):
            return True
        else:
            return False


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
