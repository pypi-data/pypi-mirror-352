# VipHL Library

A high-performance trading indicator library with source code protection.

## Installation

```bash
pip install viphl
```

## Usage

```python
from indicators.viphl.dto.viphl_interface import VipHL
import pandas as pd

# Load your price data
# Example data format: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns
data = pd.read_csv('price_data.csv')

# Initialize VipHL
viphl = VipHL()

# Calculate indicators
result = viphl.calculate(data)

# Access results
print(result)
```

## Features

- High-performance implementation with Cython
- Protected source code
- Easy-to-use API
- Compatible with pandas DataFrames

## License

Proprietary - All rights reserved. 