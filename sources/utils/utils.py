
import os
import re
from urllib.parse import urlparse
from requests import get
import exrex
import string

# disable future warning
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def load_raw_data(raw):
    data = dict()
    if not raw:
        return data
    if re.findall(r"\??(?:&?[^=&]*=[^=&]*)*", raw):
        # data is form urlencoded
        for elements in raw.split("&"):
            elements = elements.split("=")
            if len(elements)==1:
                value = ""
            else:
                value = elements[1]
            data.update({elements[0]:value})
    else:
        #data is JSON ?
        try:
            data = json.loads(raw)
        except :
            data = dict()
            print("Data given couldn't be understood")
    return data

def clear_url(url):
    url = urlparse(url)
    return f"{url.netloc}{url.path}"

def clean_end_parameters(trigger_param):
    """
    Used to clean the final big dict with all the parameters for each method & targets
    """
    for method in trigger_param:
        for target in trigger_param[method]:
            seen_params_name = list()
            seen_params = set()
            for parameter in trigger_param[method][target]:
                if not parameter.get_name() in seen_params_name:
                    seen_params_name.append(parameter.get_name())
                    seen_params.add(parameter)
                else:
                    seen_params = list(seen_params)
                    for p_index in range(0,len(seen_params)):
                        if seen_params[p_index].get_name() == parameter.get_name():
                            if seen_params[p_index].get_potential_value() == "DummyValue" and\
                                parameter.get_potential_value() != "DummyValue":
                                seen_params[p_index].set_potential_value(parameter.get_potential_value())
                    seen_params = set(seen_params)

            trigger_param[method][target] = seen_params
    return trigger_param

def split_with_final_len(list_, final_len, payload_len, prefix, suffix):
    """
    Splits "list_" into small lists with the len of pack_
    returns the list splitted
    """
    packs = list()
    end_list = list()
    length = 0
    prefix_len = len(prefix) if prefix else 0
    suffix_len = len(suffix) if suffix else 0
    for p in list_:
        # si l'url +  la longeur finale de notre pack si on ajoute le param +
        # (la longueur de payload souhaitée + prefix + suffixe * le nombre de params) + (x * "= et &" -> 2* len(packs)) est <= la longeur finale voulue
        if ((length + len(p)) + (payload_len + prefix_len + suffix_len) * len(packs) + len(packs) * 2) <= final_len:
            # actualisation de la longueur de la chaine
            # add du paramètre a la liste
            length += len(p)
            packs.append(p)
        else:
            # add du pack a la liste finale de packs
            end_list.append(packs)
            # reset des vars
            packs = list()
            length = 0
            length += len(p)
            packs.append(p)
    end_list.append(packs)
    return end_list

def open_and_split(file):
    if not file or file == "":
        return None
    opener = file_opener(file, "r")
    result = opener.read().strip().splitlines()
    opener.close()
    return result

def file_opener(file, mode):
    try:
        return open(file, mode)
    except FileNotFoundError:
        print(f"Could not open your file {file} with mode: {mode}")
        exit()

def open_distant_and_split(path):
    if not path:
        return None
    try:
        file = get(path, allow_redirects=True, verify=False)
        payloads = file.text
    except Exception as e:
        print(e)
        return None
    return payloads.strip().splitlines()

def clean(text, tag_type="name", tag_name="(c|x)srf"):
    """
    Remove values that trigger the text difference for useless reason
    i.e: xsrf csrf & misc tokens
    :returns the text cleaned
    """
    text = re.sub(
        f"<[^>].*{tag_type}=[\s]*[\"'].*{tag_name}[\"'].*[^<]>", '', text, flags=re.IGNORECASE)
    return text

def big_to_splitted(list_, pack_len):
    """
    Splits "list_" into small lists with the len of pack_len
    """
    return [list_[x:x + pack_len] for x in range(0, len(list_), pack_len)]


def big_to_splitted_dict(dict_, pack_len):
    """
    Splits "dict_" into small lists xith the len of pack_len
    """
    return [dict(list(dict_.items())[x:x+pack_len]) for x in range(0, len(dict_), pack_len)]

def random_gen(i):
    """
    : returns a string (uppercase+lowercase+numbers) of the length of "i"
    """
    return random_gen_from_regex("[a-zA-Z0-9]{"+str(i)+"}")

def random_gen_from_regex(pattern):
    """
    Return one occurence of the given pattern
    """
    return exrex.getone(pattern)

def random_gen_nums(i):
    """
    : returns a string (digits only) of the length of "i"
    """
    return random_gen_from_regex("[0-9]{"+str(i)+"}")

def create_dirs(filepath):
    """
    create the complete path to the file
    """
    components = filepath.split("/")
    components_dirs = components[:-1]
    path = ""
    for dirs in components_dirs:
        path += dirs+"/"
        try:
            os.mkdir(path)
        except:
            pass

def clean_bytes(text):
    """
    Clean the wordlist using the hard way since urllib.parse's urlencode doesn't work againt weird chars.
    """
    offsets = [i for i in range(len(text)) if not text[i] in string.printable]
    text = list(text)
    for off in offsets:
        text[off] = str(bytes(text[off], 'utf-8')).replace("\\x","%")
    return "".join(text)

def parse_url_for_params(url):
    params = set()
    for p in urlparse(url).query.split("&"):
        params.add(p.split("=")[0])
    return params

def find_trigger(text, triggers, ignorecase=False, regex=False, needs_return=False):
    """
    Used to find if a specific list of triggers is matched in some text

    :returns True or False or the match if needed
    """
    if not regex:
        if isinstance(triggers, list):
            temp_results = None
            for trigger in triggers:
                if not trigger in text:
                    return False
                else:
                    temp_results = trigger
            if not needs_return:
                return True
            else:
                return_state = temp_results
        else:
            if triggers in text:
                if not needs_return:
                    return True
                else:
                    return triggers
            return False
    else:
        flags = re.IGNORECASE
        if isinstance(triggers, list):
            has_false = False
            temp_results = None
            for trigger in triggers:
                reg = re.compile(trigger, flags)
                results = re.findall(reg, text)

                if not results or len(results)<1:
                    return False
                else:
                    temp_results = results
            if not needs_return:
                return True
            else:
                return temp_results
        else:
            reg = re.compile(triggers, flags)
            results = re.findall(reg, text)
            if results and len(results)>0:
                if not needs_return:
                    return True
                else:
                    return results
            return False



def is_normal(text, encoding="utf-8"):
    """
    if error in decoding text from the encoding specified returns False, else True
    """
    try:
        text.encode(encoding)
        return True
    except UnicodeError:
        return False

def load_tag_del(tags):
    """
    loads the argument "-delete"
    :returns a dict fromt he different valiuds values specified
    """
    if tags == None:
        return False
    ret = dict()
    try:
        for a in tags.split(","):
            b = a.split(":")
            ret.update({b[0]: b[1]})
    except ValueError:
        print(f"[ERROR] You've specified a weird payload in your argument \"-delete\", please follow the help.")
        exit(42)
    return ret

def log_this(text, file_handler, color_list):
    """
    custom logger to file
    """
    # clean the potential colors
    for color in color_list:
        text = text.replace(color, "")
    # save the text
    file_handler.write(f"{text}\n")

    return
