<img src="./icon.png" alt="icon" align="right" height="175">

# Redstone Computer Utilities Python

> Python Library for [Redstone Computer Utilities](https://github.com/NKID00/redstone-computer-utilities).

[English README](./README.md) | [简体中文简介](./README.zh_cn.md)

## Highlights

- Asynchronous network communication
- User-friendly CLI
- Static typing
- High-level API

## Usage

Python 3.7.2 or newer (CPython or PyPy) is required,

```sh
pip install redstone-computer-utilities
```

or

```toml
# pyproject.toml
redstone-computer-utilities = "^0.2.0"
```

See [docs/Usage.md](./docs/Usage.md).

## Development

To build the library, Python 3.8 or newer (CPython or PyPy) and Poetry are required,

```sh
maturin build --release --out dist --find-interpreter
```

Built wheels are in `dist/`.

To install the library into the current virtual environment,

```sh
maturin develop
```

## Copyright

Copyright © 2021-2025 NKID00

Distributed under [Apache-2.0](./LICENSE).
