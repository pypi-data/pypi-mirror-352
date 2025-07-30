import re


def extract_assignment_and_matrix(input_str: str) -> tuple:
    """
    Extracts:
    - varname (or None) if the input is of the form 'varname = [ ... ]'
    - the full '[ ... ]' matrix string

    Handles:
    - optional whitespace
    - missing varname (e.g., '= [1,2]')
    - pure matrix input (e.g., '[1,2;3,4]')
    """
    input_str = input_str.strip()

    # Attempt to extract varname only if it exists before '='
    assignment_match = re.match(r'^\s*([a-zA-Z_]\w*)\s*=\s*\[', input_str)

    # Always extract the first [ ... ] substring
    start = input_str.find('[')
    end = input_str.rfind(']')

    if start == -1 or end == -1 or end < start:
        raise ValueError("Matrix brackets not found or malformed")

    varname = assignment_match.group(1) if assignment_match else None
    matrix_str = input_str[start:end + 1]

    return varname, matrix_str
