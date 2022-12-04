import asyncio
import importlib
import inspect
import pkgutil
from typing import Type

from beauty import origin
from beauty.enums import Origin
from beauty.origin import OriginBase


def _discover_origins():
    ret = {}
    for m in pkgutil.iter_modules(origin.__path__):
        mod = importlib.import_module(f"{origin.__name__}.{m.name}")
        for _, member in inspect.getmembers(mod, inspect.isclass):
            if issubclass(member, OriginBase) and member is not OriginBase:
                ret[member.origin] = member
    return ret


_origins = _discover_origins()


def get_origin(name: Origin) -> Type[OriginBase]:
    return _origins[name]


def get_origins():
    return _origins


async def run_async(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)
