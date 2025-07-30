# Solvium Python SDK

A Python library for getting rid of various types of tasks using the Solvium API.

## Features

- **Async/Sync Support**: Choose between asynchronous and synchronous methods
- **Multiple Captcha Types**: Support for _Turnstile_, _reCAPTCHA v3_, _Cloudflare_, _Vercel_, and more...
- **Proxy Support**: Built-in proxy support for API calls
- **Comprehensive Logging**: Detailed logging with _loguru_
- **Type Safety**: Full type hints for better development experience
- **Timeout Control**: Configurable timeout settings
- **Error Handling**: Robust error handling with meaningful error messages

## Installation

```bash
pip install solvium
```

## Quick Start

### Basic Usage (Synchronous)

```python
from solvium import Solvium

# Initialize the client and paste your API key from https://t.me/solvium_crypto_bot
client = Solvium(api_key="your_api_key_here")

# Solve a Turnstile captcha
solution = client.turnstile_sync(
    sitekey="0x4AAAAAAAGm-M_XhkhrEEFd",
    pageurl="https://example.com"
)

if solution:
    print(f"Captcha solved: {solution}")
else:
    print("Failed to solve captcha")
```

### Asynchronous Usage

```python
import asyncio
from solvium import Solvium

async def solve_captcha():
    # Initialize the client and paste your API key from https://t.me/solvium_crypto_bot
    client = Solvium(api_key="your_api_key_here")

    # Solve a Turnstile captcha
    solution = await client.turnstile(
        sitekey="0x4AAAAAAAGm-M_XhkhrEEFd",
        pageurl="https://example.com"
    )

    if solution:
        print(f"Captcha solved: {solution}")
    else:
        print("Failed to solve captcha")

# Run the async function
asyncio.run(solve_captcha())
```

## Configuration

### Initialization Parameters

```python
client = Solvium(
    api_key="your_api_key_here",           # Required: Your Solvium API key
    api_proxy="http://user:password@proxy:port",       # Optional: Proxy for API calls
    api_base_url="https://captcha.solvium.io/api/v1",  # Optional: Custom API URL
    timeout=120,                           # Optional: Timeout in seconds (default: 120)
    verbose=True                           # Optional: Enable detailed logging (default: False)
)
```

## API Methods

For more details on available methods, refer to the [Solvium Documentation](https://docs.solvium.io/getting-started).

## Requirements

- Python 3.8+
- httpx
- loguru

## Getting Your API Key

1. Open [Solvium | Cracker](https://t.me/solvium_crypto_bot)
2. Press the `Start` button
3. Copy your API key
4. Use it in your Solvium client initialization

## License

This project is licensed under the Apache License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
