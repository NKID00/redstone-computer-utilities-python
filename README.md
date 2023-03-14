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

Sources are in `src/redstone_computer_utilities/`.

To build the library, Python 3.7.2 or newer (CPython or PyPy) and Poetry are required,

```sh
poetry build
```

Built wheels are in `dist/`.

To install the library into the current virtual environment,

```sh
poetry install
```

## Credits

- [colorama](https://github.com/tartley/colorama), distributed under [BSD-3-Clause](https://github.com/tartley/colorama/blob/master/LICENSE.txt).
- [typing-extensions](https://github.com/python/typing_extensions), distributed under [PSF-2.0](https://github.com/python/typing_extensions/blob/main/LICENSE).

## Copyright

Copyright © 2021-2023 NKID00

Distributed under [MPL-2.0](./LICENSE).
