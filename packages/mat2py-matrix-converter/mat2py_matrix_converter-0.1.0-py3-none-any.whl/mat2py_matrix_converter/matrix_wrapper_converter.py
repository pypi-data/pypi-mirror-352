import re

def matlab_matrix_to_python(matlab_str: str) -> str:
    """
    Convert MATLAB-style matrix [a,b;c,d] into Python-style nested list [[a, b], [c, d]].
    Whitespace is stripped from all elements.
    """
    matlab_str = matlab_str.strip().rstrip(';')

    # Remove outer brackets if present
    if matlab_str.startswith('[') and matlab_str.endswith(']'):
        matlab_str = matlab_str[1:-1].strip()

    # Split into rows and clean each element
    rows = [row.strip() for row in matlab_str.split(';') if row.strip()]
    parsed_rows = [
        f"[{', '.join(e.strip() for e in row.split(','))}]"
        for row in rows
    ]

    if len(parsed_rows) == 1:
        return parsed_rows[0]  # return just the row, not nested
        
    return f"[{', '.join(parsed_rows)}]"