from __future__ import print_function
import datetime
from colored import fg, bg

import builtins as __builtin__

class Colors():
    colors = dict()
    colors["red"] = f"{fg('red')}{bg('black')}"
    colors["green"] = f"{fg('green')}{bg('black')}"
    colors["yellow"] = f"{fg('yellow')}{bg('black')}"
    colors["blue"] = f"{fg('blue')}{bg('black')}"
    colors["purple"] = f"{fg('purple_3')}{bg('black')}"
    colors["cyan"] = f"{fg('cyan')}{bg('black')}"
    colors["white"] = f"{fg('white')}{bg('black')}"
    colors["red_bg"] = f"{fg('white')}{bg('red')}"
    colors["green_bg"] = f"{fg('white')}{bg('green')}"
    colors["dark_red"] = f"{fg('dark_red_2')}{bg('black')}"
    colors["dark_green"] = f"{fg('dark_green')}{bg('black')}"
    colors["dark_blue"] = f"{fg('dark_blue')}{bg('black')}"
    colors["end"] = "\033[0m"

    def get_color(self, color_name):
        return self.colors[color_name]

class Headers():
    headers = dict()
    headers["log"] = "[LOG]"
    headers["info"] = "[INFO]"
    headers["warning"] = "[WARNING]"
    headers["error"] = "[ERROR]"
    headers["critical"] = "[CRITICAL]"
    headers["debug"] = "[DEBUG]"
    headers["success"] = "[SUCCESS]"
    headers["failure"] = "[FAILURE]"
    headers["fatal"] = "[FATAL]"
    headers["unknown"] = "[UNKNOWN]"

class Strings():
    banner = """~~~~~~~~~~~~ Supp' Truder ? ~~~~~~~~~~~~"""
    wordlist_loaded = "Wordlist loaded ! We have {payload_len} items in this wordlist !"
    results_header = f"Time\t\tPayload_index\tStatus\tLength\tResponse_time\tPayload\n{'-' * 100}"
    results = "{time}\t{payload_index:0>6}/{payload_len}\t{status}\t{length}\t{response_time}\t{payload}"
    base_request_details = """Status: {status},Content Length: {content_len},Request Time: {total_seconds},Request Text (trucated): {text_top}[...]{text_bottom}"""


def print(text, end="\n", color=None):
    color = Colors().get_color(color) if color is not None else ""
    text = f"{color}{text}{Colors().get_color('end')}"
    __builtin__.print(text, end=end)

def log(text, type="info", date=True):
    date = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]" if date else ""
    color = ""
    match type:
        case "info":
            color = "white"
        case "warning":
            color = "yellow"
        case "error":
            color = "red"
        case "critical":
            color = "red"
        case "debug":
            color = "blue"
        case "success":
            color = "green"
        case "failure":
            color = "dark_red"
        case "fatal":
            color = "red_bg"
    print(f"{date} {Headers().headers[type]}: {text}", color=color)