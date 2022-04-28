# Supp'truder
Wassupp' Truder ?

# Idea

This tool came from an idea I had while doing bugbounty. I was very dissapointed on the common tools used to fuzz the http protocol, and I wad tired of doing some bash kung-fu or firing burp each time I had to fuzz something needing some pre treatment.
That's where Supp'truder comes: It provides a unique set of tools to pre-process your payloads and some neat features that will save you some time !

If you're interested in seeing what the tool can do, look at the examples section.

# Install
## docker
### Hub:
```bash
alias supptruder="docker run -it --rm elsicarius/supptruder:latest"
supptruder <args>
```

### Sources

```bash
sudo apt install git
git clone git@github.com:ElSicarius/Supp-truder.git

cd Supp-truder/docker
docker-compose build
docker run -it --rm supptruder:latest
```

## From sources
```bash
sudo apt install git python3.10 python3-pip virtualenv
git clone git@github.com:ElSicarius/Supp-truder.git
cd Supp-truder
virtualenv -p .py3 python3.10
source .py3/bin/activate
python3 -m pip install -r requirements.txt
```

# Examples

This is where you can see what the tool is capable of, I'm going to define a use case/problem, and a way to use the tool in order to solve the case:

## Useful parameters

-R -> Generates a list of payload that matches the regex you supplied (be careful, you can create a very huge payload list very easily)

-P -> fetches a distant payload file (Accessible via HTTP)

-B -> Makes a base request and matches the responses that does not "look like" the base request (or in the other way with the parameter -m, ie match a very specific response)

-T -> use a "tamper" script that will do some pre-processing to your payload !

-r -> Load a file containing a simple request (GET or POST), then you can eather put your placeholder in the file. if you combine it with -H you can add/overwrite headers, if you add -d, you'll overwrite the POST data.

## Filters

### All in one
Lets say you want to keep all the responses that have a content-length > 3000, a response time < 3 seconds and a status code in the 20x (ie 200, 201,202...), thats simple:

Command:
```bash
python3 supptruder.py -u "https://site.com/§" -p database/paths_medium.txt -f 20x -tf "<3" -lf ">3000" 
```
### Other examples
```
-f n200 -> exclude all the statuses 200 from the output
-f n30X -f n40x -> exclude all the 300-399 ans 400-499 statuses from the output

-tf ">=3" -> match the responses that have a response time > or equal to 3 seconds
-tf "<=3" -> match the responses that have a response time < or equal to 3 seconds
-tf "=3" -> match the responses that have a response equal to 3 seconds (useless feature I know)

-lf ">=3000" -> match the responses that have a response length > or equal to 3000 
-lf "<=3000" -> match the responses that have a response length < or equal to 3000 
-lf "=3" -> match the responses that have a response length equal to 3000

```

## Database/payloads
### Local payload
You have a simple wordlist you want to use ? easy!

Command:
```bash
python3 supptruder.py -u "https://site.com/§" -p database/path_medium_raft.txt
```

### Distant payloads (or SSRF as a service, your choice)
You have a simple wordlist you want to use but you don't want to download it because.. you name it ? easy!

Command:
```bash
python3 supptruder.py -u "https://site.com/§" -P https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-1.0.txt
```

### Regex on the flight
Let's say you are like me, you love regexes because they are awesome, and you don't want to make another useless python script/bash kungfu to generate a list of known, pattern generated, payloads.

That's very simple. Consider te following link: `https://site.com/index.php?userid=U001`

You want to discover quickly potential other users accessible via the parameter userid ? Easy !

If you are not very familiar with regexes, to generate all the possible combinaisons possible of the users (ie: U0001, U0002, ...) You need to match the "U", then 4 times a numeric value, so the regex will look like this: "U[\d]{4}".

Command:
```bash
python3 supptruder -u "https://site.com/index.php?userid=§" -R "U[\d]{4}"
```
That's it !!

## Payload tampering
### Base64 encoding 
Lets start with something simple: Consider the following url: `https://site.com/index.php?image_favicon=<base64 encoded string of "/images/favicon.ico">`

You have a payload list with tome files to try, but they need to be base64 encoded. No problem !

Command: 
```bash
python3 supptruder.py -u "https://site.com/index.php?image_favicon=§" -p database/path_medium_raft.txt -T base64
```
That's it !

### Url encoding 
Lets start with something simple: Consider the following url: `https://site.com/index.php?image_favicon=%2Fimages%2Ffavicon%2Eico`.

You have a payload list with tome files to try, but they need to be url encoded or maybe doubleUrlEncoded. No problem !

Command: 
```bash
python3 supptruder.py -u "https://site.com/index.php?image_favicon=§" -p database/path_medium_raft.txt -T urlEncode
```
That's it !

### JWT encoding 
Lets start with something simple: Consider the following url: `https://site.com/index.php` and the following header: `Authorization: JWT <jwt_token>`.
Once decoded, you found that the JWT is a simple json string: `{"username": "superName"}` and you found the key to generate more tokens ! Very nice ! But how to find more users implemented in the system ? That's simple. Open the tamper script "jwtEncode.py" located in the folder `tampers/`, and change the default key with the one you've recovered. Then:

Command: 
```bash
python3 supptruder.py -u "https://site.com/index.php" -H "Authorization: JWT §" -p database/common_usernames.txt --prefix '{"username": "' --suffix '"}' -T jwtEncode
```
That's it !

## Base requests matching
Here we can use a small "brain" to match(or not match) a specific page.

Lets say you have this url: `http://site.com/index.php?r=login`. You are looking for other pages that **does not** match the response, so status code different, or response time different or maybe different content ! (not only content length, I mean difference in the text himself !)
that's easy too !

Command:
```bash
python3 supptruder.py -u "http://site.com/index.php?r=§" -b "login" -B -p database/paths_medium.py 
```

The "-b" option defines the default payload to generate the base request

The -B option enables the base request feature

You can tweak the parameters to do things like:
-m Match exacty the base request

-mh Match also the headers, so you can detect changes in some headers like for example a "set-cookie"
-eh Exclude a header to the -mh option: for instance, to reduce the risk of getting false positives, you can exclude the "x-CSRF" or "Date"

That's it !

## Fuzzing recursive
So you have a timebased injection or a boolean based injection (Ldap/SQL/whatever). You re planning to create a script designed to fuzz this specific endpoint ? just don't :) here is how:

In this example, we are in a ldap injection, in the field "password". We know that this password is based on the chars a-Z 0-9 and {}-_ 

I'm using the negative match against a base request, which means I'm matching everything that does **not** looks like the base request, headers included (-mt, except the headers "Date" and "CSRF" with option -eh)

Then i'm activating the fuzz recursive, with a spacer null between matches ( option "--fuzz-recursive-separator" defaults to "", if you set it to "," for example, all the positive matches will be joined around the "," character). 
Finally, the --fuzz-recursive-position defines where we append the payload for the next payloads (example, <found payload><separator><next payload> for prefix or <next payload><separator><found payload> for suffix)

Command:
```bash
python3 supptruder.py -u "http://127.0.0.1:31145/login" -R "[a-zA-Z\d\{\}\_\-]" -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=§*" -B -mh -eh Date -eh "CSRF" --fuzz-recursive --fuzz-recursive-separator "" --fuzz-recursive-position "prefix" 
```

## Misc
So, in this case, you have a complex request with a ton of cookies and headers, and a huge data set. You can easily create a super complex command ans use it, or you can simply dump the request into a file, and process it with -r.

Command:
```bash
python3 supptruder.py -r request_file.txt -p database/payload.txt --force-ssl
```

There are a lot of new options, like the fact that you can send a request to a specific url and Fuzz the host header:

Command:
```bash
python3 supptruder.py -r request_file.txt -ur https://site.com/ -p database/vhosts.txt -H "Host: §"
```

# Usage (from --help)

```
usage: supptruder.py [-h] [-u URL] [-r RAW_REQUEST] [-d DATA] [-H HEADERS]
                     [-S PLACEHOLDER] [--force-ssl] [-ur URL_RAW]
                     [--fuzz-recursive]
                     [--fuzz-recursive-position {prefix,suffix}]
                     [--fuzz-recursive-separator FUZZ_RECURSIVE_SEPARATOR]
                     [--shuffle] [-v] [-t THREADS] [--throttle THROTTLE] [-re]
                     [-P DISTANT_PAYLOAD] [-R REGEX_PAYLOAD] [-p PAYLOAD]
                     [--prefix PREFIX] [--suffix SUFFIX] [--offset OFFSET]
                     [--timeout TIMEOUT] [--retry] [--verify-ssl] [-X METHOD]
                     [-f FILTER] [-T TAMPER] [-ut] [-tf TIME_FILTER]
                     [-lf LENGTH_FILTER] [-B] [-b BASE_PAYLOAD]
                     [--ignore-base-request] [-timed TIME_DIFFERENCE]
                     [-textd TEXT_DIFFERENCE_RATIO] [--ratio-type RATIO_TYPE]
                     [-m] [-mh] [-eh EXCLUDE_HEADERS]

~~~~~~~~~~ WASSUP Truder ?? ~~~~~~~~~~

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Url to test
  -r RAW_REQUEST, --raw-request RAW_REQUEST
                        Raw request prepared with the placeholder
  -d DATA, --data DATA  Add POST data
  -H HEADERS, --headers HEADERS
                        Add extra Headers (syntax: -H "test: test" -H "test2:
                        test3")
  -S PLACEHOLDER, --placeholder PLACEHOLDER
  --force-ssl           Force https when using raw-request
  -ur URL_RAW, --url-raw URL_RAW
                        Force usage of a specific URL to make the raw request.
                        Default: Using the Host header
  --fuzz-recursive      Fuzz recursively by appending positive results to
                        'prefix' or 'suffix' and starting over (useful when
                        doing timebased things/boolean based things)
  --fuzz-recursive-position {prefix,suffix}
                        Select the position where the matching payload will be
                        appended
  --fuzz-recursive-separator FUZZ_RECURSIVE_SEPARATOR
                        Set a character/string beteen positive recursive
                        matches
  --shuffle             Shuffle the payload list
  -v, --verbosity       verbosity level (3 levels available)
  -t THREADS, --threads THREADS
                        number of threads to use, default 10
  --throttle THROTTLE   throttle between the requests, default 0.0
  -re, --allow-redirects
                        Allow HTTP redirects
  -P DISTANT_PAYLOAD, --distant-payload DISTANT_PAYLOAD
                        use an online wordlist instead of a local one (do not
                        use if your internet connection is shit, or the
                        wordlist weight is like To)
  -R REGEX_PAYLOAD, --regex-payload REGEX_PAYLOAD
                        use a regex to create your payload list
  -p PAYLOAD, --payload PAYLOAD
                        payload file
  --prefix PREFIX       Prefix for all elements of the wordlist
  --suffix SUFFIX       Suffix for all elements of the wordlist
  --offset OFFSET       Offset to start from in the wordlist
  --timeout TIMEOUT
  --retry
  --verify-ssl
  -X METHOD, --method METHOD
                        HTTP method to use
  -f FILTER, --filter FILTER
                        Filter positives match with httpcode,to exclude one,
                        prefix "n", examples: -f n204 -f n403
  -T TAMPER, --tamper TAMPER
                        Use tamper scripts located in the tamper directory
                        (you can make your own)
  -ut, --untamper       Unprocess tampered payload to see what is the real
                        payload unprocessed
  -tf TIME_FILTER, --time-filter TIME_FILTER
                        Specify the time range that we'll use to accept
                        responses (format: >3000 or <3000 or =3000 or >=3000
                        or <=3000
  -lf LENGTH_FILTER, --length-filter LENGTH_FILTER
                        Specify the length range that we'll use to accept
                        responses (format: >3000 or <3000 or =3000 or >=3000
                        or <=3000
  -B, --use-base-request
                        Use the strategy to compare responses agains a base
                        request to reduce noise
  -b BASE_PAYLOAD, --base-payload BASE_PAYLOAD
                        Payload for base request
  --ignore-base-request
                        Force testing even if base request failed
  -timed TIME_DIFFERENCE, --time-difference TIME_DIFFERENCE
                        Define a time difference where base_request will not
                        be equal to the current_request, ie base request took
                        1 second and current took 2 seconds, they are
                        different until time_different>=1
  -textd TEXT_DIFFERENCE_RATIO, --text-difference-ratio TEXT_DIFFERENCE_RATIO
                        Define a text difference where base_request.text will
                        not be equal to the current_request.text, ie
                        base_request matches current_request at 98%, they are
                        different until time_different>=0.98
  --ratio-type RATIO_TYPE
                        Use a quick ratio of a normal one, quick is faster,
                        normal is for very short pages
  -m, --match-base-request
                        Match the base request to find pages identical to your
                        base payload
  -mh, --match-headers  Extends the match algorithm to the headers
  -eh EXCLUDE_HEADERS, --exclude-headers EXCLUDE_HEADERS
                        Exclude a header while extending the match algorithm
                        to the headers

```

# Todo
- Add Tampers scripts
- Use the verbosity system
- Improve the code
- Fix some bugs
- Enjoy the free time this tool gave me