# kajaani-passgen

A simple Python library to generate secure random passwords.

## Installation

```bash
pip install kajaani-passgen
```

## Usage

```python
from kajaani-passgen import generate_password

password = generate_password(length=16, use_digits=True, use_specials=True)
print(password)
```

## Features

- Control password length
- Optionally include digits and special characters
