import re

def extract_matlab_variable_names(matrix_str: str) -> list[str]:
    """
    Extracts all variable names from a MATLAB-style matrix string,
    excluding known built-in math functions (e.g., sin, cos, tan, etc.).

    Returns a sorted list of unique variable names.
    """
    # Common MATLAB built-in function names to ignore
    matlab_builtins = {
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh', 'exp', 'log', 'log10',
        'sqrt', 'abs', 'round', 'floor', 'ceil',
        'mod', 'rem', 'sign'
    }

    # Match variable names with or without indexing
    pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*(?=\()|\b([a-zA-Z_]\w*)\b')

    raw_matches = pattern.findall(matrix_str)

    vars_found = set()
    for g1, g2 in raw_matches:
        varname = g1 or g2
        if varname and varname not in matlab_builtins:
            vars_found.add(varname)

    return sorted(vars_found)