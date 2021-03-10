
import string

import difflib
import random
from statistics import mean
from sources.settings.COLORS import *
from sources.utils import *


class DiffLibrary():
    """
    Class defining the diff pseudo library used everywhere in the code
    """
    def __init__(self, session):
        """
        keep some args from settings
        """
        super().__init__(session)
        self.SESSION = session
        # shortcuts from config
        self.verbosity = self.SESSION.Conf.settings_["VERBOSITY"].verbosity
        self.difference = self.SESSION.Conf.settings_["DIFFLIB"].difflib_difference or 0.99
        self.quick_ratio = self.SESSION.Conf.settings_["DIFFLIB"].difflib_quick_ratio
        self.difftimer = self.SESSION.Conf.settings_["DIFFLIB"].difflib_difftimer
        self.del_tag = self.SESSION.Conf.settings_["DIFFLIB"].difflib_delete_html_tag
        self.debug = self.SESSION.Conf.settings_["VERBOSITY"].verbosity
        self.digfurther = self.SESSION.Conf.settings_["PROGRAM"].program_dig_further_brothers
        self.del_line = None


    def text_differ(self, text1, text2, params=None):
        # We'll not use "Real_quick_ratio" instead of "quick_ratio"
        # This would be needed because a page with a small length could be hard to match at +98% with an other page
        # Eg: page1 = "abcd" page2 = "abce"; difference = 1 caracter but match is 75% !
        # but MEH ! it's http pages we'll assume the content is >>> 4 caracters ;)
        # delete tags based on user's input
        if self.del_tag:
            for tag in self.del_tag:
                text1 = clean(text1, tag_type=tag,
                              tag_name=self.del_tag[tag])
                text2 = clean(text2, tag_type=tag,
                              tag_name=self.del_tag[tag])
        if self.del_line:
            text1 = "".join(text1.splitlines()[:sef.del_line]+text1.splitlines()[sef.del_line+1:])
            text2 = "".join(text2.splitlines()[:sef.del_line]+text2.splitlines()[sef.del_line+1:])
        if params:
            text1 = re.sub(f"\?{list(params.keys())[0]}.*{params[list(params.keys())[-1]]}","",text1)
        if self.quick_ratio:
            # diff object to be returned
            difference_of_text = difflib.SequenceMatcher(
                None, text1, text2).real_quick_ratio()
        else:
            difference_of_text = difflib.SequenceMatcher(
                None, text1, text2).quick_ratio()
        return difference_of_text

    def is_identical(self, current_req, base_request, base_reflexions=0):
        """
        Here we'll assume that two pages with text matching each other by > 98% are identical
        The purpose of this comparison is to assume that pages can contain variables like time,
        IP or the parameter itself, we don't want to match everything because there is a slightly difference between the origin request and the payloady request.

        So to be sure we don't match random things, we'll do a comparison with the value of args "textDifference"

        :returns a diff object that defines the method, the value & the boolean state of the difference
        """
        # Low cost checks
        # bn = Base none
        if base_request == False:
            self.SESSION.printcust(
                f"{color_light_blue}[DEBUG] Trigger difference: base_request = None", v=10)
            return Difference("bn", -1, False)
        # cn = current none
        if current_req == False:
            self.SESSION.printcust(
                f"{color_light_blue}[DEBUG] Trigger difference: current_req = None", v=10)
            return Difference("cn", -1, False)

        # e = equal
        if base_request.text == current_req.text:
            #return Difference("e", -1, True)
            return True

        diff_timer_requests = abs(int(base_request.elapsed.total_seconds(
        )) - int(current_req.elapsed.total_seconds()))

        difference_of_text = self.text_differ(
            base_request.text, current_req.text)
        # d = diff
        if base_request.status_code == current_req.status_code and difference_of_text >= self.difference:
            #return Difference("d", difference_of_text, True)
            return True
        else:
            # 6
            self.SESSION.printcust(
                f"{color_light_blue}[DEBUG] Trigger difference: status 1:{base_request.status_code},2:{current_req.status_code},text diff: {difference_of_text}", v=10)
            if self.debug:
                temp = ""
                for line in difflib.unified_diff(base_request.text, current_req.text):
                    temp += line
            return Difference("d", difference_of_text, False)
        # t = timer
        if diff_timer_requests >= self.difftimer:
            self.SESSION.printcust(
                f"{color_light_blue}[DEBUG] Trigger difference: timercause", v=10)
            return Difference("t", diff_timer_requests, False)
        # n = None,nothing, nullos...
        return True
        #return Difference("n", -1, True)

class Difference(DiffLibrary):
    """
    Difference objects to keep the details of our differencies
    """
    def __init__(self, diff_, value, bool_val):
        """
        Values needed in the whole class
        """
        self.value = value
        self.diff = diff_
        self.bool_val = bool_val
        return

    def diff_type(self):
        """
        Returns diff type by it's letter
        """
        return self.diff

    def diff_value(self):
        """
        Returns the potential value of the difference (ie: number of reflexion)
        """
        return self.value

    def equals(self, diff_obj):
        """
        Helps to compare two diff objects
        returns a boolean value
        """
        if diff_obj.diff_type() == self.diff and diff_obj.diff_value() == self.value:
            return True

        """
        if diff_obj.diff_type() == self.diff:
            return True
        """
        return False

    def __str__(self):
        return f"diff type: {self.diff},value {self.value }, state: {self.bool_val}"

    def __bool__(self):
        return self.bool_val

    __nonzero__ = __bool__
