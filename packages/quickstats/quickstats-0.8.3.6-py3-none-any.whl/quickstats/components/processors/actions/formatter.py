import re

from quickstats.utils.string_utils import split_str, str_to_bool

ListRegex = re.compile(r"\[([^\[\]]+)\]")

def ListFormatter(text:str):
    if not isinstance(text, str):
        return text
    match = ListRegex.match(text)
    if not match:
        return [text]
    return split_str(match.group(1), sep=',', strip=True, remove_empty=True)

def BoolFormatter(text:str):
    return str_to_bool(text)