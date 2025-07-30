# MATLAB-to-Python Matrix Converter

This library provides a set of utility functions to **convert MATLAB-style matrix expressions into valid Python/NumPy/Torch formats**. It handles common indexing, matrix formatting, and math function conversion tasks, allowing MATLAB snippets to be reused directly in Python with minimal manual adjustment.

---

## Features

- **Index Conversion:** Converts MATLAB's `x(i)` (1-based) indexing to Python's `x[i-1]` (0-based).
- **Matrix Format Conversion:** Transforms MATLAB matrices like `[1,2;3,4]` into Python-style `[[1, 2], [3, 4]]`.
- **Variable Extraction:** Identifies all variable names used in a matrix expression, excluding common math functions.
- **Matrix Assignment Parsing:** Extracts both variable name and raw matrix string from MATLAB-style assignment lines.
- **Torch-Compatible Output:** Provides a full example that outputs `torch.tensor(...)` objects from MATLAB expressions.

---

## Files Overview

### `index_converter.py`

Converts `varname(n)` to `varname[n-1]` using regex. Useful for transforming MATLAB indexing syntax.

```python
convert_idx_for_var(expr: str, varname: str) -> str
```

---

### `matrix_wrapper_converter.py`

Converts MATLAB matrix string format `[a,b;c,d]` to Python-style nested lists.

```python
matlab_matrix_to_python(matlab_str: str) -> str
```

---

### `variable_extractor.py`

Parses a matrix string and extracts all variable names (excluding built-ins like `sin`, `cos`, etc.).

```python
extract_matlab_variable_names(matrix_str: str) -> list[str]
```

---

### `extract_raw_matrix_str.py`

Extracts the variable name and raw matrix string from an input line such as:

```matlab
M = [1, 2; 3, 4]
```

Even supports anonymous matrices (`=[...]` or `[...]`).

```python
extract_assignment_and_matrix(input_str: str) -> tuple
```

---

### `general.py`

Takes in string of Matlab matrix and return string of the matrix represented as a tensor:

```matlab
M = [1, 2; 3, 4]
```

Even supports anonymous matrices (`=[...]` or `[...]`).

```python
matlab_to_tensor(input_str: str) -> str
```

---

### `example.py`

A full demo that:
1. Extracts the matrix.
2. Replaces MATLAB operations (e.g., `.*`, `.^`).
3. Converts trigonometric functions to `torch.` variants.
4. Converts indexing, and matrix format.
5. Returns a `torch.tensor(...)` result.

---

## Example Usage

```python
from mat2py_matrix_converter import matlab_to_tensor, extract_matlab_variable_names

matlab_code = "M = [1, 2; 3, 4];"
vars = extract_matlab_variable_names(matlab_code)
py_tensor = matlab_to_tensor(matlab_code)
```
