<img src="./icon.png" alt="图标" align="right" height="175">

# Redstone Computer Utilities Python

> 配合 [Redstone Computer Utilities](https://github.com/NKID00/redstone-computer-utilities) 使用的 Python 库。

[English README](./README.md) | [简体中文简介](./README.zh_cn.md)

## 亮点

- 异步网络通信
- 友好的控制台界面
- 静态类型检查
- 高阶 API

## 用法

需要安装 Python 3.7.2 或更新版本（CPython 或 PyPy），

```sh
pip install redstone-computer-utilities
```

或者

```toml
# pyproject.toml
redstone-computer-utilities = "^0.2.0"
```

详见 [docs/Usage.md](./docs/Usage.zh_cn.md)。

## 开发

要构建此库，需要安装 Python 3.7.2 或更新版本（CPython 或 PyPy）和 Poetry，

```sh
poetry build
```

构建出的 wheel 文件位于 `dist/`。

要安装此库到当前的虚拟环境，

```sh
poetry install
```

## 鸣谢

- [colorama](https://github.com/tartley/colorama)，使用 [BSD-3-Clause](https://github.com/tartley/colorama/blob/master/LICENSE.txt) 许可证分发。
- [typing-extensions](https://github.com/python/typing_extensions)，使用 [PSF-2.0](https://github.com/python/typing_extensions/blob/main/LICENSE) 许可证分发。

## 版权

版权所有 © 2021-2023 NKID00

使用 [MPL-2.0](./LICENSE) 许可证分发。
