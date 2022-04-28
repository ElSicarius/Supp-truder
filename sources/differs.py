
import difflib

class Differs():

    def __init__(self, base_payload, time_difference, text_difference_ratio=0.98, ratio_type="quick"):
        self.base_payload = base_payload
        self.time_difference = time_difference
        self.text_difference_ratio = text_difference_ratio
        self.ratio_type = ratio_type
        pass
    
    def is_identical(self, base_request, request2, payload_to_remove:str(), match_headers=False, exclude_headers=[]):
        """
        Here we'll assume that two pages with text matching each other by > 98% are identical
        The purpose of this comparison is to assume that pages can contain variables like time,
        IP or the parameter itself, we don't want to match everything because there is a slightly difference between the origin request and the payloady request.

        So to be sure we don't match random things, we'll do a comparison with the value of args "textDifference"
        """
        exclude_headers = [x.lower() for x in exclude_headers]
        if base_request.text.replace(self.base_payload, "") == request2.text.replace(payload_to_remove, "") and not match_headers:
            return True
        diff_timer_requests = abs(base_request.elapsed.total_seconds() - request2.elapsed.total_seconds())

        if diff_timer_requests >= self.time_difference:
            return False
        # We'll not use "Real_quick_ratio" instead of "quick_ratio"
        # This would be needed because a page with a small length could be hard to match at +98% with an other page
        # Eg: page1 = "abcd" page2 = "abce"; difference = 1 caracter but match is 75% !
        # but MEH ! it's http pages we'll assume the content is > 4 caracters ;)
        text1 = base_request.text
        text2 = request2.text
        if match_headers:
            for header, value in base_request.headers.items():
                if not header.lower() in exclude_headers:
                    text1 = text1 + f"{header}: {value}"
            for header, value in request2.headers.items():
                if not header.lower() in exclude_headers:
                    text2 = text2 + f"{header}: {value}"
        if len(self.base_payload) > 4:
            text1 = text1.replace(self.base_payload, "")
        if len(payload_to_remove) > 4:
            text2 = text2.replace(payload_to_remove, "")
        if self.ratio_type == "quick":
            
            difference_of_text = difflib.SequenceMatcher(
                None, text1, text2).quick_ratio()
        else:
            difference_of_text = difflib.SequenceMatcher(
                None, text1, text2).ratio()

        if base_request.status_code == request2.status_code:
            if difference_of_text > self.text_difference_ratio:
                return True
        return False