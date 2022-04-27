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

That's it !

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

# Todo
- Add Tampers scripts
- Use the verbosity system
- Improve the code
- Fix some bugs
- Enjoy the free time this tool gave me