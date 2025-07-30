# ALU math matrices multiplication

A lightweight Python library to multiply two matrices of any compatible size.

## Example

```python
pip install alumath_group12
```

```python

from alumath_group12 import multiply_matrices

a = [
    [2, 4, 1],
    [0, 3, 5],
    [7, 1, 6]
]

b = [
    [1, 0, 2],
    [3, 5, 6],
    [4, 7, 8]
]

result = multiply_matrices(a, b)
print(result)

```
