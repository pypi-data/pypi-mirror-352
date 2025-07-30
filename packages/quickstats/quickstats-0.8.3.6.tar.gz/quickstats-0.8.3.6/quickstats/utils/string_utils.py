from typing import Optional, Callable, List, Dict
import re
import ast
import uuid
import string

import numpy as np

formatter = string.Formatter()

def split_lines(s: str, comment_string: Optional[str] = "#", remove_blank: bool = True,
                with_line_number: bool = False, keepends: bool = False):
    """
    Split a multi-line string into individual lines and optionally remove comments and/or blank lines.

    Parameters:
        s (str): The input multi-line string to be split.
        comment_string (Optional[str], optional): The string representing the start of a comment line.
                                                  Lines starting with this string will be considered as comments 
                                                  and removed. Defaults to "#".
        remove_blank (bool, optional): If True, remove blank lines (lines containing only whitespace).
                                       Defaults to True.
        with_line_number (bool, optional): If True, returns a list of tuples with line numbers and lines.
                                           If False, returns a list of lines. Defaults to False.
        keepends (bool, optional): If True, the line breaks are included in each line. If False, line breaks 
                                   are removed. Defaults to False.

    Returns:
        list or list of tuples: A list of lines from the input string. If 'with_line_number' is True, 
                                it returns a list of tuples with line numbers and lines.
    """
    lines = s.splitlines(keepends=keepends)

    if comment_string:
        lines = [line.split(comment_string, 1)[0] for line in lines]

    if remove_blank and with_line_number:
        lines = [(line, i + 1) for i, line in enumerate(lines) if line.strip()]
    elif remove_blank:
        lines = [line for line in lines if line.strip()]
    elif with_line_number:
        lines = [(line, i + 1) for i, line in enumerate(lines)]
        
    return lines


def split_str(s: str, sep: str = None, strip: bool = True, remove_empty: bool = False, cast: Optional[Callable] = None,
              use_paranthesis:bool = False, empty_value:Optional[str]='') -> List:
    """
    Splits a string and applies optional transformations.

    This function splits a string into a list where each element is a substring of the 
    original string. By default, it trims leading and trailing whitespace from each substring. 
    It can also optionally remove empty substrings and apply a casting function to each substring.

    Parameters
    ----------
    s : str
        The string to split.
    sep : str, optional
        The separator according to which the string is split. If not specified or None, 
        the string is split at any whitespace. Defaults to None.
    strip : bool, optional
        Whether to trim leading and trailing whitespace from each substring. Defaults to True.
    remove_empty : bool, default = False
        Whether to remove empty substrings from the list. Defaults to False.
    cast : Callable, optional
        An optional casting function to apply to each substring. It should be a function 
        that takes a single string argument and returns a value. Defaults to None.
    use_paranthesis: bool, default = False
        Whether to ignore separator within paranthesis.
    empty_value: str, optional, default = ''
        Replace empty token with this value.

    Returns
    -------
    list
        A list of substrings (or transformed substrings) obtained by splitting the input string.
    """
    if use_paranthesis:
        if sep is None:
            raise ValueError('separator can not be None when "use_paranthesis" option is set to True')
        items = re.split(sep + r'\s*(?![^()]*\))', s)
    else:
        items = s.split(sep)
    if strip:
        items = [item.strip() for item in items]
    if remove_empty:
        items = [item for item in items if item]
    if cast is None:
        cast = lambda x: x
    items = [cast(item) if item else empty_value for item in items]

    return items
    
whitespace_trans = str.maketrans('', '', " \t\r\n\v")
newline_trans = str.maketrans('', '', "\r\n")

def remove_whitespace(s: str) -> str:
    """
    Removes all whitespace characters from a string.

    The function effectively removes characters like space, tab, carriage return, 
    newline, and vertical tab from the provided string.

    Parameters
    ----------
    s : str
        The input string from which to remove whitespace.

    Returns
    -------
    str
        The string with all whitespace characters removed.
    """
    return s.translate(whitespace_trans)

def remove_newline(s: str):
    """
    Removes newline characters from a string.

    Parameters:
        s (str): The input string from which to remove newline characters.

    Returns:
        str: The input string with all newline characters removed.
    """
    return s.translate(newline_trans)

neg_zero_regex = re.compile(r'(?![\w\d])-(0.[0]+)(?![\w\d])')

def remove_neg_zero(s:str):
    """
    Replaces instances of negative zero in a string with zero.
    
    Parameters:
        string (str): The input string in which to replace negative zeros.

    Returns:
        str: The input string with all instances of negative zero replaced with zero.

    Example:
        string = "The temperature is -0.000 degrees."
        print(remove_neg_zero(string))
        # outputs: "The temperature is 0.000 degrees."
    """
    return neg_zero_regex.sub(r'\1', s)


def parse_as_dict(s:str, item_sep:str=',', key_value_sep:str='='):
    """
    Parse a string into a dictionary based on given item and key-value separators.

    Parameters
    ----------
    s : str
        The input string to be parsed into a dictionary.
    item_sep : (optional) str, default = ','
        The separator between items
    key_value_sep : (optional) str, default = '='
        The separator between keys and values

    Returns
    -------
    dict
        A dictionary containing the parsed key-value pairs.

    Examples
    --------
    >>> parse_as_dict("name='John',age=25")
    {'name': 'John', 'age': 25}
    """
    tokens = split_str(s, sep=item_sep, strip=True, remove_empty=True)
    result = {}
    for token in tokens:
        subtokens = split_str(token, sep=key_value_sep, strip=True)
        if len(subtokens) != 2:
            raise ValueError(f'invalid key-value format: {token}')
        key, value = subtokens
        if key in result:
            raise RuntimeError(f'multiple values specified for the key "{key}"')
        result[key] = ast.literal_eval(value)
    return result
    
    
def make_multiline_text(text: str, max_line_length: int, break_word: bool = True, indent: str = '') -> str:
    """
    Formats a given text into multiple lines with a specified maximum line length and optional indentation.

    Parameters
    ----------
    text : str
        The input text to be formatted.
    max_line_length : int
        The maximum length of each line.
    break_word : bool, optional
        Whether to break words if they exceed the maximum line length. Default is True.
    indent : str, default = ''
        The string used to indent lines after the first line.

    Returns
    -------
    str
        The formatted text with lines of specified maximum length and indentation.
    """
    if break_word:
        n = max_line_length
        lines = [text[i:i + n] for i in range(0, len(text), n)]
        if indent > 0:
            lines = [lines[0]] + [(" " * indent) + line for line in lines[1:]]
        return '\n'.join(lines)
    
    # Accumulated line length
    indent_length = len(indent)
    acc_length = indent_length
    words = text.split(" ")
    formatted_text = ""
    first_line = True
    
    for word in words:
        # If accumulated length plus length of word and a space is less than or equal to max line length
        if acc_length + (len(word) + 1) <= max_line_length:
            # Append the word and a space
            formatted_text += word + " "
            # Update accumulated length
            acc_length += len(word) + 1
        else:
            # Append a line break, then the word and a space
            formatted_text += "\n" + indent + word + " "
            # Reset counter of length to the length of the word and a space
            acc_length = len(word) + indent_length + 1
    
    return formatted_text.lstrip("\n")

def insert_breaks_preserving_words(text: str, max_width: int, indent: str) -> str:
    """
    Inserts line breaks into a string to ensure it fits within a specified width without breaking words.
    Subsequent lines are indented with the given indent string.

    Args:
        text: The original string to process.
        max_width: The maximum width of each line, in characters.
        indent: The string used to indent lines after the first line.

    Returns:
        The modified string with line breaks and indentation inserted.
    """
    words = text.split()
    if not words:
        return ""

    current_line = words[0]
    formatted_lines = []

    for word in words[1:]:
        # Check if adding the next word would exceed the max width
        if len(current_line) + len(word) + 1 <= max_width:
            current_line += " " + word
        else:
            formatted_lines.append(current_line)
            current_line = indent + word
            max_width = len(indent) + max_width  # Adjust max_width for indentation
    formatted_lines.append(current_line)  # Add the last line

    return "\n".join(formatted_lines)

def get_field_names(format_str: str) -> List[str]:
    """
    Extracts field names from a format string.

    Parameters
    ----------
    format_str : str
        The format string containing fields to extract.

    Returns
    -------
    list
        A list of field names found in the format string.
    """
    field_names = [field_name for _, field_name, _, _ in formatter.parse(format_str) if field_name]
    return field_names

def parse_format_str_with_regex(str_list, format_str, regex_map, mode: str = "search"):
    """
    Extracts format string field attributes from regex patterns.

    Parameters
    ----------
    str_list : list or str
        A list of strings or a single string to be parsed.
    format_str : str
        The format string containing fields to extract.
    regex_map : dict
        A dictionary mapping field names to their corresponding regex patterns.
    mode : str, optional
        The regex matching mode. It must be one of "search", "match", or "fullmatch". Default is "search".

    Returns
    -------
    list
        A list of tuples where each tuple contains a string and a dictionary of extracted field values.

    Raises
    ------
    ValueError
        If the mode is not one of "search", "match", or "fullmatch".
        If a field in the format string does not have a corresponding regex pattern in the regex_map.
    """
    if isinstance(str_list, str):
        return parse_format_str_with_regex([str_list], format_str, regex_map)
    
    if mode not in ["search", "match", "fullmatch"]:
        raise ValueError('mode must be one of "search", "match", or "fullmatch"')
    
    field_names = get_field_names(format_str)
    unique_fields, counts = np.unique(field_names, return_counts=True)
    field_groupkeys = {}
    duplicate_groupkey_maps = {}
    format_pattern = str(format_str)
    
    for i, field in enumerate(unique_fields):
        if field not in regex_map:
            raise ValueError(f'missing regex pattern for the field: "{field}"')
        
        pattern = regex_map[field]
        groupkeys = list(re.compile(pattern).groupindex.keys())
        field_groupkeys[field] = groupkeys
        count = counts[i]
        
        for j in range(count):
            pattern_ = pattern
            if j > 0:
                suffix = unique_string()
                for groupkey in groupkeys:
                    if groupkey not in duplicate_groupkey_maps:
                        duplicate_groupkey_maps[groupkey] = []
                    new_groupkey = f"{groupkey}_{suffix}"
                    duplicate_groupkey_maps[groupkey].append(new_groupkey)
                    pattern_ = pattern_.replace(f"(?P<{groupkey}>", f"(?P<{new_groupkey}>")
            format_pattern = format_pattern.replace(f"{{{field}}}", pattern_, 1)
    
    regex = re.compile(format_pattern)
    method = getattr(regex, mode)
    results = []
    
    for str_ in str_list:
        match = method(str_)
        if not match:
            continue
        
        groupdict = match.groupdict()
        valid_match = True
        
        for key, altkeys in duplicate_groupkey_maps.items():
            if not all(groupdict[key] == groupdict[altkey] for altkey in altkeys):
                valid_match = False
                break
            for altkey in altkeys:
                groupdict.pop(altkey)
        
        if not valid_match:
            continue
        
        result = (str_, groupdict)
        results.append(result)
    
    return results

def format_delimited_dict(dictionary: dict, separator: str = '=', delimiter: str = ',') -> str:
    """
    Formats a dictionary into a string, where each key-value pair is separated by the specified
    separator, and different items are separated by the specified delimiter.

    Parameters
    ----------
    dictionary : dict
        The dictionary to format.
    separator : str, optional
        The string used to separate keys from values. Defaults to '='.
    delimiter : str, optional
        The string used to separate different key-value pairs. Defaults to ','.

    Returns
    -------
    str
        The formatted string where keys and values are joined by the separator, and items are separated
        by the delimiter.

    Example
    -------
    >>> format_delimited_dict({'key1': 'value1', 'key2': 'value2'}, '=', ',')
    'key1=value1,key2=value2'
    """
    return delimiter.join([f"{key}{separator}{value}" for key, value in dictionary.items()])

def format_aligned_dict(dictionary: Dict[str, str], separator: str = " : ",
                        left_margin: int = 0, linebreak: int = 100) -> str:
    """
    Formats a dictionary into a neatly aligned string representation, with each key-value pair on a new line. 

    Args:
        dictionary: The dictionary to format. Keys should be strings, and values are expected to be strings that 
                    can contain multiple words.
        separator: The string used to separate keys from their values. Defaults to ": ".
        left_margin: The number of spaces to prepend to each line for indentation. Defaults to 0.
        linebreak: The maximum allowed width of each line, in characters, before wrapping the text to a new line. 
                    Defaults to 100.

    Returns:
        A string representation of the dictionary. Each key-value pair is on its own line, with lines broken such 
        that words are not split across lines, respecting the specified `linebreak` width.

    Example:
        >>> example_dict = {"Key1": "This is a short value.", "Key2": "This is a much longer value that will be wrapped according to the specified line break width."}
        >>> print(format_aligned_dict(example_dict, left_margin=4, linebreak=80))
         Key1: This is a short value.
         Key2: This is a much longer value that will be wrapped according to the
               specified line break width.

    Note:
        The function removes existing newlines in values to prevent unexpected line breaks and treats the entire 
        value as a single paragraph that needs to be wrapped according to `linebreak`.
    """
    if not dictionary:
        return ""

    max_key_length = max(len(key) for key in dictionary)
    indent_size = left_margin + max_key_length + len(separator)
    effective_text_width = linebreak - indent_size

    if effective_text_width <= 0:
        raise ValueError("Line break width must be greater than the size of indentation and separator.")

    formatted_lines = []
    indent_string = " " * indent_size
    for key, value in dictionary.items():
        cleaned_value = str(value).replace("\n", " ")
        wrapped_value = make_multiline_text(cleaned_value, linebreak, False, indent_string)
        line = f"{' ' * left_margin}{str(key):{max_key_length}}{separator}{wrapped_value}"
        formatted_lines.append(line)

    return "\n".join(formatted_lines) + "\n"


def str_to_bool(s: str) -> bool:
    """
    Convert a string into a boolean value.

    Parameters
    ----------
    s : str
        The string to convert.

    Returns
    -------
    bool
        The boolean value of the string.
    """
    s = s.strip().lower()
    if s in {'true', '1'}:
        return True
    elif s in {'false', '0'}:
        return False
    raise ValueError(f"Invalid literal for boolean: '{s}'")

def remove_cpp_type_casts(expression: str) -> str:
    """
    Removes type casts from a C/C++ expression based on general structure.

    Parameters
    ----------
    expression : str
        A string containing a C/C++ expression.

    Returns
    -------
    str
        The expression with type casts removed.
    """
    # Matches a parenthetical that seems like a type (any word potentially followed by pointer/reference symbols),
    # ensuring it's not preceded by an identifier character and is followed by a valid variable name.
    type_cast_pattern = r'(?<![\w_])\(\s*[a-zA-Z_]\w*\s*[\*&]*\s*\)\s*(?=[a-zA-Z_]\w*|[+-]?\s*\d|\.)'
    return re.sub(type_cast_pattern, '', expression)

def extract_variable_names(expression:str)->List[str]:
    """
    Extracts variable names from a C/C++ expression.

    Parameters:
    expression (str): A string containing a C/C++ expression.

    Returns:
    list: A list of unique variable names found in the expression.
    """

    expression = remove_cpp_type_casts(expression)

    # Match potential variable names which are not directly followed by a '(' which would indicate a 
    # function call. Use negative lookaheads and positive lookbehinds to refine the match.
    pattern = r'\b[a-zA-Z_]\w*(?:\.\w+)*\b(?!\s*\()'

    matches = re.findall(pattern, expression)

    from quickstats.utils.common_utils import remove_duplicates
    unique_matches = remove_duplicates(matches)
    
    return unique_matches

def replace_with_mapping(s: str, mapping: Dict[str, str]) -> str:
    """
    Replaces substrings in the input string based on a given mapping.

    Parameters
    ----------
    s : str
        The input string in which substrings will be replaced.
    mapping : Dict[str, str]
        A dictionary where the keys are substrings to be replaced and the values are the substrings to replace them with.

    Returns
    -------
    str
        The modified string with replacements made based on the mapping.
    """
    for old, new in mapping.items():
        s = s.replace(old, new)
    return s

def indent_str(s: str, indent: int = 4, indent_char: str = ' ') -> str:
    """
    Indents each line of a given string.

    Parameters
    ----------
    s : str
        The input string to be indented.
    indent : int, optional
        The number of characters to indent each line. Default is 4.
    indent_char : str, optional
        The character used for indentation. Default is a space (' ').

    Returns
    -------
    str
        The indented multi-line string.

    Examples
    --------
    >>> s = "Line 1\nLine 2\nLine 3"
    >>> indent_str(s, indent=4, indent_char=' ')
    '    Line 1\n    Line 2\n    Line 3'

    >>> indent_str(s, indent=2, indent_char='-')
    '--Line 1\n--Line 2\n--Line 3'
    """
    indentation = indent_char * indent
    return '\n'.join([f'{indentation}{line}' for line in s.splitlines()])

class PartialFormatter:
    """
    A string formatter that allows partial formatting with a subset of keys.
    Missing keys are left with their placeholder intact.
    Double braces {{}} are preserved as literal braces.

    Example usage:
        pf = PartialFormatter()
    
        # Partially format only 'name', leaving rank with its spec
        s = "Hello {name:s}, your rank is {rank:2d}!"
        partially_done = pf.format(s, name="Alice")
        print(partially_done)  
        # "Hello Alice, your rank is {rank:2d}!" (still has :2d)
    
        # Then finalize it, supplying the missing field
        final = pf.format(partially_done, rank=3)
        print(final)
        # "Hello Alice, your rank is  3!"   (padded to width 2)
    
        # Check double braces remain intact
        test_braces = "Here is a double brace: {{should_not_change}}"
        print(pf.format(test_braces))
        # "Here is a double brace: {{should_not_change}}"
    """
    
    def __init__(self, missing_key_handler=None):
        """
        Initialize the formatter.
        
        Args:
            missing_key_handler (callable, optional): Function to handle missing keys.
                If provided, it will be called with the missing key name and should
                return the string to use in place of the missing key.
        """
        self.missing_key_handler = missing_key_handler

    def _get_field(self, field_name, format_spec, conversion, kwargs):
        """
        Get the string to insert for the given field.
        - If the field is found in kwargs, apply any conversion and format_spec.
        - If missing, return the original placeholder, preserving !r, :2f, etc.
        """
        # Build the placeholder back in case it's missing:
        # e.g. {field_name!r:2f}, {rank}, {value:02d}, etc.
        if conversion:
            missing_placeholder = f"{{{field_name}!{conversion}"
        else:
            missing_placeholder = f"{{{field_name}"
        if format_spec:
            missing_placeholder += f":{format_spec}"
        missing_placeholder += "}"

        # If the field is missing, either use a handler or preserve the placeholder
        if field_name not in kwargs:
            if self.missing_key_handler is not None:
                return self.missing_key_handler(field_name)
            return missing_placeholder

        # Field is present: apply conversion and format it
        val = kwargs[field_name]

        # Apply Python-style conversion
        # (string.Formatter supports '!r' and '!s'; anything else is custom.)
        if conversion == 'r':
            val = repr(val)
        elif conversion == 's':
            val = str(val)

        # If there's a format spec (e.g. ":02d"), apply it
        if format_spec:
            return format(val, format_spec)
        else:
            # No format spec, just convert to string
            return str(val)

    def format(self, format_string, **kwargs):
        """
        Format a string with the given keyword arguments.
        Missing keys will have their placeholders preserved.
        Double braces {{}} are preserved as literal braces.
        
        Args:
            format_string (str): The string to format
            **kwargs: Keyword arguments for formatting
            
        Returns:
            str: The partially or fully formatted string
        """
        # Temporary markers to protect double braces
        tmp_open = "\uE000"
        tmp_close = "\uE001"
        
        # Replace {{ with a marker
        format_string = format_string.replace("{{", tmp_open)
        # Replace }} with a marker
        format_string = format_string.replace("}}", tmp_close)
        
        result_pieces = []
        
        # Use Python's built-in formatter parsing
        for literal_text, field_name, format_spec, conversion in formatter.parse(format_string):
            # Always append the literal text first
            if literal_text:
                result_pieces.append(literal_text)
            
            # If there's a field, get the (possibly partially) formatted version
            if field_name is not None:
                piece = self._get_field(field_name, format_spec, conversion, kwargs)
                result_pieces.append(piece)
        
        # Join all pieces
        formatted_result = "".join(result_pieces)
        
        # Restore the original double braces
        formatted_result = formatted_result.replace(tmp_open, "{{")
        formatted_result = formatted_result.replace(tmp_close, "}}")
        
        return formatted_result
    
    def is_fully_formatted(self, string: str) -> bool:
        """
        Check if a string contains any remaining unformatted placeholders.
        
        Args:
            string (str): The string to check
            
        Returns:
            bool: True if the string is fully formatted, False otherwise
        """
        # Remove double-brace placeholders first
        tmp_string = string.replace("{{", "").replace("}}", "")
        
        return not any(
            field_name is not None
            for _, field_name, _, _ in formatter.parse(tmp_string)
        )

partial_formatter = PartialFormatter()
partial_format = partial_formatter.format

class PlainStr(str):
    """
    A string class where the `repr` of the string is the same as its `str` representation.
    """

    def __repr__(self) -> str:
        """
        Returns the same output as `str` for the representation.

        Returns
        -------
        str
            The string representation of the object.
        """
        return str(self)

def unique_string() -> str:
    return uuid.uuid4().hex