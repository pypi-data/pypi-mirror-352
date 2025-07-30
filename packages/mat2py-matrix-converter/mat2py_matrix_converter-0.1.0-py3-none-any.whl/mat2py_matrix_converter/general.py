import re
from mat2py_matrix_converter.extract_raw_matrix_str import extract_assignment_and_matrix
from mat2py_matrix_converter.index_converter import convert_idx_for_var
from mat2py_matrix_converter.matrix_wrapper_converter import matlab_matrix_to_python
from mat2py_matrix_converter.variable_extractor import extract_matlab_variable_names

# convert matlab matrix to torch.tensor

def matlab_to_tensor(str):

    # get varname and raw matrix
    varname, mat = extract_assignment_and_matrix(str)

    # get rid of whitespace
    mat = ''.join(mat.split())

    # change .^ to **
    mat = mat.replace(".^", "**")

    # change .* to *
    mat = mat.replace(".*", "*")

    # add torch. to sin and cos, tan, cot
    mat = mat.replace("sin", "torch.sin")
    mat = mat.replace("cos", "torch.cos")
    mat = mat.replace("tan", "torch.tan")
    mat = mat.replace("cot", "torch.cot")

    # change x(i) to x[i-1] for all vars
    variables = extract_matlab_variable_names(mat)
    for v in variables:
        mat = convert_idx_for_var(mat, v)

    # change matlab matrix to python matrix
    mat = matlab_matrix_to_python(mat)

    out = "torch.tensor(" + mat + ")"

    return out