import re

# a variable name is a word that does not start with a number
varname_pattern = r'\b[a-zA-Z_]\w*\b'

def is_valid_variable(expr: str) -> bool:
    return re.fullmatch(varname_pattern, expr) is not None
