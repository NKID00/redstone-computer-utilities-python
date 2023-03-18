from __future__ import annotations
import io
import threading
import time
from typing import Any, NoReturn, Optional, TextIO, cast
import itertools
import sys
import signal

import colorama


_wrapper: CliIOWrapper
_cli_lock = threading.Lock()
_stdout: TextIO


def _ctrlc_handler(_signum, _frame):
    _wrapper.clear_message()
    sys.stdout = _stdout
    info('  Stopped')
    sys.exit(0)


def init() -> None:
    global _wrapper
    colorama.init()
    _wrapper = CliIOWrapper(sys.stdout, '', '')
    signal.signal(signal.SIGINT, _ctrlc_handler)
    threading.Thread(target=_cli_daemon, daemon=True).start()


def _endswith_line_break(s: str) -> bool:
    return s.endswith(('\r', '\n'))


class CliIOWrapper:
    def __init__(self, inner: TextIO, message: str, spinner: str) -> None:
        self._inner = inner
        self._buffer = io.StringIO()
        self._last_message = f'{spinner} {message}'
        self._spinner = spinner
        self.message = message

    def clear_message(self) -> None:
        # add more spaces to clear ^C
        print(
            '\r', ' ' * (len(self._last_message) + 4),
            end='\r', file=self._inner)

    def _print_message(self) -> None:
        if len(self._last_message) - len(self._message):
            self.clear_message()
        s = f'\r{self.spinner} {self._message}'
        print(s, end='', file=self._inner)
        self._last_message = s[1:]

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, s: str) -> None:
        self._message = s
        self._print_message()

    @property
    def spinner(self) -> str:
        return self._spinner

    @spinner.setter
    def spinner(self, spinner: str) -> None:
        self._spinner = spinner
        self._print_message()

    def write(self, s: str) -> int:
        with _cli_lock:
            if s == '':
                return 0
            lines = s.splitlines(True)
            if len(lines) > 1 or _endswith_line_break(lines[0]):
                lines[0] = self._buffer.getvalue() + lines[0]
                self._buffer = io.StringIO()
                self.clear_message()
                if _endswith_line_break(lines[-1]):
                    self._inner.write(
                        ''.join(map(lambda s: '  ' + s, lines)))
                else:
                    self._inner.write(
                        ''.join(map(lambda s: '  ' + s, lines[:-1])))
                    self._buffer.write(lines[-1])
                self._print_message()
            else:
                self._buffer.write(s)
            return len(s)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


SPINNER_ITER = itertools.cycle('⠸⢰⣠⣄⡆⠇⠋⠙')


def _cli_daemon() -> NoReturn:
    global _stdout
    _stdout = sys.stdout
    sys.stdout = cast(TextIO, _wrapper)

    while True:
        with _cli_lock:
            _wrapper.spinner = next(SPINNER_ITER)
        time.sleep(0.1)


def print_colored(color: str, *values: object, sep: Optional[str] = None,
                  end: Optional[str] = None) -> None:
    if len(values) == 0:
        return
    elif len(values) == 1:
        print(color + str(values[0]) + colorama.Fore.RESET, end=end)
    else:
        print(color + str(values[0]), *values[1:-1],
              values[-1] + colorama.Fore.RESET, sep=sep, end=end)


def info(*values: object, sep: Optional[str] = None,
         end: Optional[str] = None) -> None:
    print(*values, sep=sep, end=end)


def warn(*values: object, sep: Optional[str] = None,
         end: Optional[str] = None) -> None:
    print_colored(colorama.Fore.YELLOW, *values, sep=sep, end=end)


def error(*values: object, sep: Optional[str] = None,
          end: Optional[str] = None) -> None:
    print_colored(colorama.Fore.RED, *values, sep=sep, end=end)


def message(message: str) -> None:
    with _cli_lock:
        _wrapper.message = message
