import pathlib
import sys
from dataclasses import fields
from typing import List
from typing import Optional

from .schemas import BaseInfo
from .schemas import detect_schema

if sys.version_info >= (3, 12):
    # https://docs.python.org/3/whatsnew/3.12.html
    # -> The pathlib.Path class now supports subclassing

    class ESRFPath(pathlib.Path):
        __slots__ = ("_esrf_info",)

        def __init__(self, *args):
            super().__init__(*args)
            _add_esrf_info(self, *args)

        def __getattr__(self, name: str) -> Optional[str]:
            if self._esrf_info and hasattr(self._esrf_info, name):
                return getattr(self._esrf_info, name)
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        def __dir__(self) -> List[str]:
            if self._esrf_info:
                esrf_info_attrs = {field.name for field in fields(self._esrf_info)}
            else:
                esrf_info_attrs = set
            return sorted(set(super().__dir__()) | esrf_info_attrs)

        @property
        def esrf_info(self) -> Optional[BaseInfo]:
            return self._esrf_info

else:

    class ESRFPath(type(pathlib.Path())):
        __slots__ = ("_esrf_info",)

        def __new__(cls, *args):
            self = super().__new__(cls, *args)
            _add_esrf_info(self, *args)
            return self

        def __dir__(self) -> List[str]:
            if self._esrf_info:
                esrf_info_attrs = {field.name for field in fields(self._esrf_info)}
            else:
                esrf_info_attrs = set
            return sorted(set(super().__dir__()) | esrf_info_attrs)

        def __getattr__(self, name: str) -> Optional[str]:
            if self._esrf_info and hasattr(self._esrf_info, name):
                return getattr(self._esrf_info, name)
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        @property
        def esrf_info(self) -> Optional[BaseInfo]:
            return self._esrf_info

        @classmethod
        def _from_parts(cls, args, **kwargs):
            self = super()._from_parts(args, **kwargs)
            _add_esrf_info(self, *args)
            return self

        @classmethod
        def _from_parsed_parts(cls, drv, root, parts):
            self = super()._from_parsed_parts(drv, root, parts)
            _add_esrf_info(self)
            return self


def _add_esrf_info(self: ESRFPath, *args) -> None:
    self._esrf_info = None
    esrf_info = detect_schema(str(self))
    if esrf_info is None:
        for arg in args:
            if isinstance(arg, ESRFPath):
                esrf_info = arg._esrf_info
                if esrf_info is not None:
                    break
    self._esrf_info = esrf_info
