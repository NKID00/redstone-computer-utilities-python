'''redstone-computer-utilities

Simple debug tools for redstone computers.'''

__all__ = ['Script', 'Vec3i', 'Interval', 'gametick', 'redstonetick', 'second', 'Interface', 'info', 'warn', 'error']

__version__ = '0.2.0'

from .main import Script
from .datatype import Vec3i, Interval, gametick, redstonetick, second, Interface
from .cli import info, warn, error
