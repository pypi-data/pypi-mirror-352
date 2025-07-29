# Simple Stats

A simple Python library for basic statistical calculations.

## Features

- Calculate mean
- Calculate median
- Calculate mode
- Calculate standard deviation

## Installation

You can install the library using pip:

```bash
pip install common-stats-test
```

## Example Code

```python
from common_stats import mean, median, mode, standard_deviation

data = [1, 3, 3, 3, 5]

print("Mean:", mean(data))
print("Actual Mean: 3.")
print("Median:", median(data))
print("Actual Median: 3.")
print("Mode:", mode(data))
print("Actual Mode: 3.")
print("Standard Deviation:", standard_deviation(data))
```
