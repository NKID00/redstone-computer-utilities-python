import asyncio
import json
import sys
from typing import Callable, NoReturn, Awaitable, Any, Optional, Union
import threading
from collections import defaultdict
import urllib.parse

import websockets

from .datatype import (
    Pos, Vec3i, Interface, BlockUpdateType, AlarmAt,
    ApiException, ApiExceptions, Interval)
from .util import base64_to_int, int_to_base64, bytes_to_base64
from . import cli


class Event:
    def __init__(self, name: str, param: Optional[dict] = None) -> None:
        self._name = name
        self._param = {} if param is None else param
        self._param_json = json.dumps(
            self.param, sort_keys=True,
            ensure_ascii=False, separators=(',', ':'))

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Event)
                and self._name == other._name
                and self._param == other._param)

    def __hash__(self) -> int:
        return hash((self._name, self._param_json))

    def __str__(self) -> str:
        if self._param is None:
            return self._name
        return f'{self._name}({self.param})'

    def __repr__(self) -> str:
        if self._param is None:
            return f'Event({self._name!r})'
        return f'Event({self._name!r}, {self._param!r})'

    @property
    def name(self) -> str:
        return self._name

    @property
    def param(self) -> Any:
        return self._param


class Script:
    def __init__(self, name: str, description: str = '') -> None:
        self._name: str = name
        self._description: str = description
        self._loop: asyncio.AbstractEventLoop
        self._websocket: websockets.WebSocketClientProtocol
        self._event_callback: defaultdict[
            Event, list[Callable]] = defaultdict(list)
        self._running: bool = False
        self._thread_local = threading.local()

    @property
    def running(self) -> bool:
        return self._running

    def _recv(self, timeout: Optional[float] = 2) -> dict:
        return json.loads(self._await(self._websocket.recv(), timeout))

    def _recv_and_process_event(self, timeout: Optional[float] = 2) -> dict:
        '''Returns until API call result arrives or timeout'''
        while True:
            message = self._recv(timeout)
            if 'event' in message:
                try:
                    result = self._dispatch_event(
                        Event(message['event'], message['param']),
                        message['content'])
                except ApiException as e:
                    self._send({'finish': e.code})
                else:
                    self._send({'finish': result})
            else:
                result = message['result']
                if isinstance(result, int):
                    raise ApiException(result)
                else:
                    return result

    def _send(self, message: dict) -> None:
        self._await(self._websocket.send(json.dumps(
            message, ensure_ascii=False, separators=(',', ':'))))

    def _call_api(self, name: str, param: dict) -> dict:
        self._send({'api': name, 'param': param})
        return self._recv_and_process_event()

    def _finish_event(self, result: Union[dict, int]) -> None:
        self._send({'finish': result})

    def _await(self, awaitable: Awaitable, timeout: Optional[float] = 2) -> Any:
        '''Execute an awaitable synchronously'''
        try:
            return self._loop.run_until_complete(
                asyncio.wait_for(awaitable, timeout))
        except TimeoutError:
            # TODO: handle timeout
            exit(1)

    def run(self, key: str = '', host: str = '') -> NoReturn:
        '''Runs the script and connect to host (default to 'localhost:37265')
        with the provided key.'''
        cli.init()
        if host == '':
            if len(sys.argv) > 1:
                host = sys.argv[1]
            else:
                host = 'localhost:37265'
        cli.message(f'Connecting to {host}')
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        name = urllib.parse.quote_plus(self._name)
        description = urllib.parse.quote_plus(self._description)
        key = urllib.parse.quote_plus(key)
        self._websocket = self._await(websockets.connect(
            f'ws://{host}/?name={name}&{description}&key={key}'))
        self._running = True
        cli.message('Running')
        cli.info(f'Connected to {host}')
        self._recv_and_process_event(timeout=None)
        raise IOError('Invalid message')  # unreachable

    def _subscribe(self, event: Event) -> None:
        self._call_api('subscribe', {'name': event.name, 'param': event.param})

    def new_interface(self, name: str, lsb: Pos, msb: Pos, option: list[str]) -> None:
        raise NotImplementedError()

    def remove_interface(self, name: str) -> None:
        raise NotImplementedError()

    def list_interface(self, name: str) -> None:
        raise NotImplementedError()

    def read_interface(self, name: str) -> int:
        return base64_to_int(self._call_api('readInterface', {'name': name})['value'])

    def write_interface(self, name: str, value: Union[int, bytes]) -> None:
        if isinstance(value, bytes):
            v = bytes_to_base64(value)
        else:
            v = int_to_base64(value)
        self._call_api('writeInterface', {'name': name, 'value': v})

    def query_gametime(self) -> int:
        return self._call_api('queryGametime', {})['gametime']

    def execute_command(self, command: str) -> None:
        raise NotImplementedError()

    def info(self, message: str) -> None:
        cli.info(message)
        self._call_api('log', {'message': message, 'level': 'info'})

    def warn(self, message: str) -> None:
        cli.warn(message)
        self._call_api('log', {'message': message, 'level': 'warn'})

    def error(self, message: str) -> None:
        cli.error(message)
        self._call_api('log', {'message': message, 'level': 'error'})

    def _dispatch_event(self, event: Event, content: dict) -> dict:
        args: list = []
        if event.name == 'scriptInitialize':
            for e in self._event_callback.keys():
                if e.name != 'scriptInitialize':
                    self._subscribe(e)
            for callback in self._event_callback[event]:
                self._execute_callback(callback, args)
            cli.info('Initialized')
            return {}
        elif event.name == 'scriptRun':
            for arg in content['argument']:
                if isinstance(arg, str):
                    args.append(arg)
                else:
                    args.append(Interface(arg))
            r = 0
            for callback in self._event_callback[event]:
                t = self._execute_callback(callback, args)
                if t is not None:
                    r += t
            return {'result': r}
        else:
            if event.name == 'interfaceChange':
                args = [
                    base64_to_int(content['previous']),
                    base64_to_int(content['current'])]
            for callback in self._event_callback[event]:
                self._execute_callback(callback, args)
            return {}

    def _execute_callback(self, callback: Callable, args: list) -> Any:
        result: list = []
        detach = threading.Event()
        threading.Thread(
            target=self._callback_thread_entry,
            args=(callback, args, result, detach)).start()
        if not detach.wait(timeout=2):
            # TODO: handle timeout
            exit(1)
        if len(result) > 0:
            return result[0]
        else:
            return None

    def _callback_thread_entry(
            self, callback: Callable, args: list,
            result: list,
            detach: threading.Event) -> None:
        self._thread_local.detach = detach
        t = callback(*args)
        if not self._thread_local.detach.is_set():
            result.append(t)
            self._thread_local.detach.set()

    def _decorator(
            self, event: Event) -> Callable[[Callable], Callable]:
        def inner(func):
            nonlocal self, event
            if self.running and event not in self._event_callback:
                self._event_callback[event].append(func)
                self._subscribe(event)
            else:
                self._event_callback[event].append(func)
            return func
        return inner

    def on_script_initialize(self):
        return self._decorator(Event('scriptInitialize'))

    def on_script_run(self):
        return self._decorator(Event('scriptRun'))

    def on_interface_change(self, name: str):
        return self._decorator(Event('interfaceChange', {'name': name}))

    def on_block_update(self, pos: Pos, type_: BlockUpdateType):
        return self._decorator(
            Event('blockUpdate', {'pos': pos, 'type': type_.value}))

    def on_alarm(self, gametime: int, at: AlarmAt = AlarmAt.START):
        return self._decorator(
            Event('alarm', {'gametime': gametime, 'at': at.value}))

    def wait(self, interval: Interval, at: AlarmAt = AlarmAt.START):
        alarm_hook_event = threading.Event()
        next_detach_handle = []

        @self.on_alarm(self.query_gametime() + interval.gametick, at)
        def alarm_hook():
            nonlocal next_detach_handle
            next_detach_handle.append(self._thread_local.detach)
            alarm_hook_event.set()
            self._thread_local.detach.wait()

        self._thread_local.detach.set()
        alarm_hook_event.wait()
        self._thread_local.detach = next_detach_handle[0]

