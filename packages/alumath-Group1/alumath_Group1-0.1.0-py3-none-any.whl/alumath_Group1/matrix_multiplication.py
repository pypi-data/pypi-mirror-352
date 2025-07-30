#!usr/bin/bash
def multiply_matrices(matrix_a, matrix_b):
    """
    Performs matrix multiplication on two matrices.

    Args:
        matrix_a (list of lists): The first matrix.
        matrix_b (list of lists): The second matrix.

    Returns:
        list of lists: The resulting matrix after multiplication.

    Raises:
        ValueError: If the matrices cannot be multiplied (inner dimensions do not match).
    """
    rows_a = len(matrix_a)
    cols_a = len(matrix_a[0])
    rows_b = len(matrix_b)
    cols_b = len(matrix_b[0])

    if cols_a != rows_b:
        raise ValueError("Matrices dimensions are incompatible for multiplication. "
                         "Number of columns in matrix A must equal number of rows in matrix B.")

    # Initialize the result matrix with zeros
    result_matrix = [[0 for _ in range(cols_b)] for _ in range(rows_a)]

    # Perform matrix multiplication
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a): # or rows_b, they are equal
                result_matrix[i][j] += matrix_a[i][k] * matrix_b[k][j]
    return result_matrix
