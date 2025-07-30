from alumath_group12 import multiply_matrices

def test_basic_multiplication():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    result = multiply_matrices(a, b)
    assert result == [[19, 22], [43, 50]]