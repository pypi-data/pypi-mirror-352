# shansort

**Unified fast radix sort for int, float, and string in Python**

`shansort` provides a blazing fast sorting function implemented in C++ with `pybind11`, using radix sort optimized for integers, floating-point numbers, and ASCII strings.

## How It Works

`shansort` uses radix sort algorithms specialized for three data types:

- **Integers:** Uses a 64-bit radix sort based on XOR with the sign bit to handle negative numbers correctly.
- **Floats:** Converts floats to sortable 64-bit keys via bit manipulations that preserve the order, then applies radix sort.
- **Strings:** Performs LSD (least significant digit) radix sort on ASCII characters from the end of the strings, handling variable lengths efficiently.

Before sorting, the algorithm checks if the data is already sorted ascending or descending to optimize performance.

This approach achieves high speed by avoiding comparison-based sorting and leveraging bitwise operations and counting sort passes.

## Features

- Fast radix sort specialized for int64, double, and ASCII strings
- Handles sorted, reverse sorted, and unsorted data efficiently
- Python interface: `shansort.sort(list)` supports int, float, or string lists
- Up to 3.7x to 5.3x faster than Python built-in `sorted()` on large datasets

## Installation

```bash
pip install shansort


import shansort

# Sort integers
ints = [5, 3, 9, 1]
print(shansort.sort(ints))  # [1, 3, 5, 9]

# Sort floats
floats = [3.14, 2.71, 1.62, 0.0]
print(shansort.sort(floats))  # [0.0, 1.62, 2.71, 3.14]

# Sort strings (ASCII only)
strings = ["banana", "apple", "cherry"]
print(shansort.sort(strings))  # ['apple', 'banana', 'cherry']


## Metrics
Benchmarking with 10,000,000 elements on a typical modern CPU:
| Data Type | Python built-in `sorted()` | `shansort.sort()` | Speedup Factor (times faster) |
| --------- | -------------------------- | ----------------- | ----------------------------- |
| Integers  | 9.78 seconds               | 1.84 seconds      | \~5.3x                        |
| Floats    | 8.82 seconds               | 1.98 seconds      | \~4.5x                        |
| Strings   | 15.60 seconds              | 4.25 seconds      | \~3.7x                        |




Algorithm Limits & Data Ranges
Supports 64-bit signed integers (int64_t) and 64-bit doubles (double).

Sorts ASCII strings only (no Unicode).

Uses 8 passes of 8 bits each (64-bit radix), so limited to 64-bit data.

Works correctly and efficiently within these ranges.