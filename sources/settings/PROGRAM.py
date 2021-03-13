# target
program_target = None
program_loaded_payloads = set()
program_raw_data = None

# defined later by processing
program_extra_data = None


# program customization
program_threads = 5
program_dump_html = False
program_replace_string = "§"
program_base_payload = "FuzzingYourApp"

# fuzzing related params
program_status_filter = list()
program_length_filter = list()
program_length_exclusion = list()
program_time_filter = list()

# wordlist related
wordlist_cleaning = False
wordlist_offset = 0
wordlist_shuffle = False

# mutations
wordlist_mutations = list()

# tampers
program_tamper = None

# regex based wordlist
program_regex_wordlist = None
