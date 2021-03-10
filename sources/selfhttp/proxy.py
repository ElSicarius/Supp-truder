import re
from urllib.request import build_opener, ProxyHandler

from sources.settings.COLORS import *
import socks
from sockshandler import SocksiPyHandler

class Proxy(str):
    """Proxy tunnel for use through urllib http tunnel. (extends str)

    Takes None or a proxy in the form <SCHEME>://<HOST>:<PORT>, where scheme
    can be http or https.
    The Proxy datatype returns an urllib opener that includes current
    proxy, or empty opener if the proxy is None.

    Example:
    >>> print(Proxy('127.0.0.1:8080'))
    "http://127.0.0.1:8080"

    """

    _match_regexp = r"^(?:(socks[45]|https?)://)?([\w.-]{3,63})(?::(\d+))$"

    # cls == slelf in PEP8 :D
    def __new__(cls, proxy=None):
        if str(proxy).lower() == 'none':
            return str.__new__(cls, 'None')

        try:
            components = list(re.match(cls._match_regexp, proxy).groups())
        except:
            synopsis = "[http(s)|socks<4|5>]://<HOST>:<PORT>"
            raise ValueError(f'Proxy invalid format (must be «{synopsis}»)')

        defaults = ['http', '', '']
        # populate proxy elements
        for index, elem in enumerate(components):
            if elem is None:
                components[index] = defaults[index]

        proxy = "{}://{}:{}".format(*tuple(components))

        return str.__new__(cls, proxy)

    def __init__(self, _=None):
        """Build self._urllib_proxy_handler"""

        proxy = super().__str__()

        if proxy == "None":
            self._urllib_proxy_handler = ProxyHandler()
            return

        components = list(re.match(self._match_regexp, proxy).groups())
        self.scheme, self.host, self.port = components
        self.components = components

        if self.scheme == "socks4":
            socks4_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS4, self.host, int(self.port))
            self._urllib_proxy_handler = socks4_handler
        elif self.scheme == "socks5":
            socks5_handler = SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, self.host, int(self.port))
            self._urllib_proxy_handler = socks5_handler
        else:
            proxy_handler = ProxyHandler({'http': proxy, 'https': proxy})
            self._urllib_proxy_handler = proxy_handler

    def _raw_value(self):
        return super().__str__()

    def __call__(self):
        return self._urllib_proxy_handler

    def __str__(self):
        if not hasattr(self, "scheme"):
            return "None"
        return f"{color_pink_bold}{self.scheme}://{color_end+color_bold}{self.host}{color_dark_blue}{self.port}{color_end}"
