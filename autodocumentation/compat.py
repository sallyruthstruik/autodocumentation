import sys

def to_unicode(s):
    if sys.version_info[0] < 3:
        if isinstance(s, str):
            return s.decode("utf-8")

    return s
