import datetime
import os
import re
from dataclasses import dataclass
from typing import Literal
from typing import Optional
from typing import Union

SEP = r"[\\/]"
NOTSEP = r"[^\\/]"


@dataclass
class BaseInfo:
    pass


_ESRF_V3 = rf"""
(?P<data_root>.*?)
{SEP}(?P<proposal>{NOTSEP}+)
{SEP}(?P<beamline>{NOTSEP}+)
{SEP}(?P<session_date>\d{{8}})
{SEP}(?P<data_type>RAW_DATA|PROCESSED_DATA|NOBACKUP|SCRIPTS)
(?:{SEP}(?P<collection>{NOTSEP}+))?
(?:{SEP}(?P=collection)_(?P<dataset>{NOTSEP}+))?
"""


@dataclass
class ESRFv3Info(BaseInfo):
    data_root: Optional[str] = None
    proposal: Optional[str] = None
    beamline: Optional[str] = None
    session_date: Optional[datetime.date] = None

    data_type: Optional[
        Literal["RAW_DATA", "PROCESSED_DATA", "NOBACKUP", "SCRIPTS"]
    ] = None
    collection: Optional[str] = None
    dataset: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.session_date, str):
            self.session_date = datetime.datetime.strptime(
                self.session_date, "%Y%m%d"
            ).date()


_ESRF_V2 = rf"""
(?P<data_root>.*?)
{SEP}(?P<proposal>{NOTSEP}+)
{SEP}(?P<beamline>{NOTSEP}+)
{SEP}(?P<session_date>\d{{8}})
{SEP}(?P<data_type>raw|processed|_nobackup)
(?:{SEP}(?P<collection>{NOTSEP}+))?
(?:{SEP}(?P=collection)_(?P<dataset>{NOTSEP}+))?
"""


@dataclass
class ESRFv2Info(BaseInfo):
    data_root: Optional[str] = None
    proposal: Optional[str] = None
    beamline: Optional[str] = None
    session_date: Optional[datetime.date] = None

    data_type: Optional[Literal["raw", "processed", "_nobackup"]] = None
    collection: Optional[str] = None
    dataset: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.session_date, str):
            self.session_date = datetime.datetime.strptime(
                self.session_date, "%Y%m%d"
            ).date()


_ESRF_V1 = rf"""
(?P<data_root>.*?)
{SEP}(?P<proposal>{NOTSEP}+)
{SEP}(?P<beamline>{NOTSEP}+)
{SEP}(?P<session_date>\d{{8}})
(?:{SEP}(?P<collection>{NOTSEP}+))?
(?:{SEP}(?P=collection)_(?P<dataset>{NOTSEP}+))?
"""


@dataclass
class ESRFv1Info(BaseInfo):
    data_root: Optional[str] = None
    proposal: Optional[str] = None
    beamline: Optional[str] = None
    session_date: Optional[datetime.date] = None

    collection: Optional[str] = None
    dataset: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.session_date, str):
            self.session_date = datetime.datetime.strptime(
                self.session_date, "%Y%m%d"
            ).date()


_SCHEMA_PATTERNS = [
    (re.compile(f"^{_ESRF_V3}", re.VERBOSE), ESRFv3Info),
    (re.compile(f"^{_ESRF_V2}", re.VERBOSE), ESRFv2Info),
    (re.compile(f"^{_ESRF_V1}", re.VERBOSE), ESRFv1Info),
]


def detect_schema(path_str: str) -> Optional[BaseInfo]:
    path_str = os.path.abspath(path_str)
    for pattern, info in _SCHEMA_PATTERNS:
        match = pattern.match(path_str)
        if match:
            groups = {k: v for k, v in match.groupdict().items() if v is not None}
            return info(**groups)


FieldValueTypes = Union[str, None]
