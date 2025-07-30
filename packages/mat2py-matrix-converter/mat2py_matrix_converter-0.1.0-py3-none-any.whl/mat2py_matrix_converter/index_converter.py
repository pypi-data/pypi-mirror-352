import re

def convert_idx_for_var(expr: str, varname: str) -> str:
    """
    Converts varname(n) to varname[n-1] for 1-based to 0-based indexing.

    Args:
        expr (str): The input expression string.
        varname (str): The variable name to look for (e.g., "x", "a", "theta").

    Returns:
        str: The converted expression.
    """

    pattern = re.compile(rf"\b{re.escape(varname)}\((\d+)\)")
    # () catpures groups, starting from 1 , index 0 is always the whole expression

    def replacer(match):
        index = int(match.group(1))
        return f"{varname}[{index - 1}]"

    return pattern.sub(replacer, expr)