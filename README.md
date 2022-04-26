# Supp'truder
Wassupp' Truder ?

# Idea

This tool came from an idea I had while doing bugbounty. I was very dissapointed on the common tools used to fuzz the http protocol, and I wad tired of doing some bash kung-fu or firing burp each time I had to fuzz something needing some pre treatment.
That's where Supp'truder comes: It provides a unique set of tools to pre-process your payloads and some neat features that will save you some time !

If you're interested in seeing what the tool can do, look at the examples section.

# Examples

This is where you can see what the tool is capable of, I'm going to define a use case/problem, and a way to use the tool in order to solve the case:

## Useful parameters

-R -> Generates a list of payload that matches the regex you supplied (be careful, you can create a very huge payload list very easily)

-P -> fetches a distant payload file (Accessible via HTTP)

-B -> Makes a base request and matches the responses that does not "look like" the base request (or in the other way with the parameter -m, ie match a very specific response)

-T -> use a "tamper" script that will do some pre-processing to your payload !

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


# Todo
- Add Tampers scripts
- Improve the code
- fix some bugs
- enjoy the free time this tool gave me