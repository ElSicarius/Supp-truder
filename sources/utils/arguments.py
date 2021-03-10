import argparse
import sys

def get_parser():
    """
    Parses the argparse object
    :returns the arguments object
    """
    if len(sys.argv) < 2:
        return None

    parser = argparse.ArgumentParser(description='SuperTruder: Fuzz something, somewhere in an URL, data or HTTP headers',
                                     epilog="Tired of using ffuf ? Tired of using burp's slow intruder ? Checkout SuperTruder, an intruder that isn't hard to use, or incredibly slow\n Made with love by Sicarius (@AMTraaaxX) ")

    # Fuzzing stuff
    parser.add_argument('-u', "--url", help='Url to test',)
    parser.add_argument('-p', "--payload", help='payload file',)
    parser.add_argument('-P', "--distant_payload",
                        help="use an online wordlist instead of a local one (do not use if your internet connection is shit, or the wordlist weight is like To)", default=False)
    parser.add_argument("-R", "--regexPayload", help="use a regex to create your payload list")
    parser.add_argument("-d", "--data", default=None, help="Add POST data")
    parser.add_argument('-b', "--basePayload",
                        help="Payload for base request", default="Fuzzing")
    parser.add_argument("-H", "--headers", default={},
                        help="Add extra Headers (syntax: \"header: value\\nheader2: value2\")")
    parser.add_argument("-S", "--replaceStr", default="§")
    parser.add_argument("-T", "--tamper",help="Use tamper scripts located in the tamper directory (you can make your own)", default=None)

    # Sorting stuff
    parser.add_argument(
        "-f", "--filter", help="Filter positives match with httpcode, comma separated, to exclude one: n200", default='any')
    parser.add_argument("-l", "--lengthFilter",
                        help='Specify the len range that we\'ll use to accept responses (eg: 0,999 or any, if 3 values, we\'ll accept EXACTLY this values)', default="any,any")
    parser.add_argument("-m", '--matchBaseRequest',
                        action="store_true", default=False)
    parser.add_argument("-el", "--excludeLength",
                        help='Specify the len range that we\'ll use to deny responses (eg: 0,999 or any, if 3 values, we\'ll refuse EXACTLY this values)', default="none,none")
    parser.add_argument(
        "-t", "--timeFilter", help='Specify the time range that we\'ll use to accept responses (eg: 0,999 or any, if 3 values, we\'ll accept EXACTLY this values)', default="any,any")

    # misc stuff
    parser.add_argument('-o', '--dumpHtml', help='file to dump html content')
    parser.add_argument(
        "--offset", help="Start over where you stopped by giving the payload offset", default=0)
    parser.add_argument("--shuffle", help="Shuffle the payload list", default=False, action="store_true")

    # request stuff
    parser.add_argument('-r', "--redir", dest="redir", default=False,
                        action="store_true", help='Allow HTTP redirects')
    parser.add_argument("--timeout", default=20)
    parser.add_argument(
        "--throttle", help="throttle between the requests", default=0.01)
    parser.add_argument("--verify", default=False, action="store_true")

    # program functionnalities
    parser.add_argument(
        "--difftimer", help="Change the default matching timer (default 2000ms -> 2 seconds)", default=2000)
    parser.add_argument(
        "--textDifference", help="Percentage difference to match pages default: 99%%", default=0.99)
    parser.add_argument("--quickRatio", help="Force quick ratio of pages (a bit faster)",
                        action="store_true", default=False)
    parser.add_argument("--threads", default=5)
    parser.add_argument("--ignoreBaseRequest", default=False,
                        action="store_true", help="Force testing even if base request failed")
    parser.add_argument("--uselessprint", help="Disable useless self-rewriting print (with '\\r')",
                        default=False, action="store_true")
    parser.add_argument("-q", "--quiet", help="tell the program to output only the results",
                        default=False, action="store_true")
    parser.add_argument("-v",'--verbosity', help="Change the verbosity of the program (available: 1,2,3)", default=2)

    return parser
