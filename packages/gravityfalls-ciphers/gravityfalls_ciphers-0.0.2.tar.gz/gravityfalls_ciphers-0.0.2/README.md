# Gravity Falls Ciphers

A Python package for encoding and decoding text inspired by the cryptographic mystery-solving elements of the TV show **Gravity Falls**.

---

## What is this?

`gravityfalls_ciphers` is a lightweight and educational Python package that lets you:

- Encrypt and decrypt messages using famous classical ciphers.
- Understand how each cipher manipulates text.
- Integrate cipher utilities into games, puzzles, learning platforms, or fun coding projects.

---

## Installation

Currently, this package is not available on PyPI. To use it:

```
pip install gravityfalls-ciphers==0.0.1
```

## Usage
```python
from gravityfalls_ciphers import GFCipher
cipher = GFCipher()
ciphered_text = cipher.caesar_encode("WELCOME TO GRAVITY FALLS")
print(ciphered_text)
# Output: ZHOFRPH WR JUDYLWB IDOOV
```

## References
https://gravityfalls.fandom.com/wiki/List_of_cryptograms/Episodes