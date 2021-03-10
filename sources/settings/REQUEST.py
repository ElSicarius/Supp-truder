
request_proxy = None

# some request linked parameters
request_max_req_per_min = 1000
request_throttle = 0.0
request_timeout = 20 # timeout of a request
request_allow_redirects = False
request_retry = False
request_limit_rate_sleep = 25

# request object parameters
request_headers = None
request_method = "GET"

# requests automation
request_use_custom_login_method = False

# used variables
request_base_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}
request_post_headers_form = {"Content-Type": "application/x-www-form-urlencoded"}
request_post_headers_xml = {"Content-Type": "application/xml"}
request_post_headers_json = {"Content-Type": "application/json"}
