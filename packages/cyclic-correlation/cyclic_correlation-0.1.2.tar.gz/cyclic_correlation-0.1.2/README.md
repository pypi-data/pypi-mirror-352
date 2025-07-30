# Cyclic Correlation Module

This module provides functions to compute the cyclic cross-correlation between two 1D signals using either FFT-based or analytic methods. It supports automatic input validation, optional zero-padding, and normalization.

## Features

- **Input validation**: Ensures signals are 1D and compatible in length.
- **Flexible methods**: Choose between `"fft"` (fast) and `"analytic"` (direct computation).
- **Padding/truncation**: Automatically pads or truncates signals to match lengths if needed.
- **Normalization**: Optionally normalizes the correlation output.

## Functions

### `cyclic_corr(s1, s2, method="fft", padded=True, normalized=True)`

Computes the cyclic cross-correlation between signals `s1` and `s2`.

#### Parameters

- `s1`, `s2`: 1D lists or numpy arrays (input signals).
- `method`: `"fft"` (default) or `"analytic"`.
- `padded`: If `True`, pads shorter signal to match the longer one.
- `normalized`: If `True`, normalizes the correlation output.

#### Returns

- `Z`: Cyclic cross-correlation array.
- `max_val`: Maximum absolute value of the correlation.
- `t_max`: Index of the maximum correlation.
- `min_val`: Minimum absolute value of the correlation.

### `check_inputs_define_limits(s1, s2, method, padded)`

Validates and prepares input signals for correlation computation.

## Example

```python
from cyclic_correlation import cyclic_corr

s1 = [1, 2, 3, 4]
s2 = [4, 3, 2, 1]
Z, max_val, t_max, min_val = cyclic_corr(s1, s2, method="fft", padded=True, normalized=True)
print("Correlation:", Z)
print("Max value:", max_val)
print("Index of max:", t_max)
print("Min value:", min_val)
```

## Requirements

- numpy

## License

BSD-3-Clause