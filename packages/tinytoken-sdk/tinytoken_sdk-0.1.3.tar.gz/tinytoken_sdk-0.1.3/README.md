# TinyToken SDK

Text compression API client.

## Install

```bash
pip install tinytoken-sdk
```

## Usage

You need an API key to use TinyToken. Get one at [https://tinytoken.org](https://tinytoken.org).

```python
import tinytoken

# Compress text using the function directly
result = tinytoken.compress("Your text here", "your-api-key")
print(result)

# Or use the class (recommended)
client = tinytoken.TinyToken("your-api-key")
result = client.compress("Your text here")
print(result)

# With optional quality parameter
result = client.compress("Your text here", quality=0.8)
print(result)
```

