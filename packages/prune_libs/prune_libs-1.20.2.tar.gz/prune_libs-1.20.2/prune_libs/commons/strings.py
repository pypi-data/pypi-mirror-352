import re


def is_valid_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False
