"""
Multiplies two matrices a and b
@param a: First matrix
@param b: Second matrix
@return: Resulting matrix after multiplication
"""

def multiply_matrices(a, b):
    if not a or not b:
        raise ValueError("Matrices should not be empty")
    
    number_of_rows_a = len(a)
    number_of_columns_a = len(a[0])
    number_of_rows_b = len(b)
    number_of_columns_b = len(b[0])
    if number_of_columns_a != number_of_rows_b:
        raise ValueError("Number of columns in the first matrix must equal the number of rows in the second matrix")
    
    result = [[0 for col in range(number_of_columns_b)] 
              for row in range(number_of_rows_a)]
    
    for i in range(number_of_rows_a):
        for j in range(number_of_columns_b):
            for k in range(number_of_columns_a):
                result[i][j] += a[i][k] * b[k][j]


    return result