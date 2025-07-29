from dataclasses import fields

import pytest

from .. import Path
from ..schemas import ESRFv1Info
from ..schemas import ESRFv2Info
from ..schemas import ESRFv3Info
from .utils import make_path
from .utils import safe_repr

TEST_PATHS = {
    make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    ): ESRFv3Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="RAW_DATA",
        collection="foo",
        dataset="bar",
    ),
    make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    ): ESRFv2Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection="foo",
        dataset="bar",
    ),
    make_path(
        "visitor", "ma6658", "id21", "20250509", "foo", "foo_bar", "foo_bar.h5"
    ): ESRFv1Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        collection="foo",
        dataset="bar",
    ),
    make_path("some", "other", "path", "that", "does", "not", "match"): None,
}


@pytest.mark.parametrize("input_path", TEST_PATHS.keys())
def test_esrf_path_esrf_info(input_path):
    path = Path(input_path)
    assert path.esrf_info == TEST_PATHS[input_path]


@pytest.mark.parametrize("input_path", TEST_PATHS.keys())
def test_esrf_path_attributes(input_path):
    path = Path(input_path)
    expected_info = TEST_PATHS[input_path]

    if expected_info is None:
        with pytest.raises(AttributeError):
            _ = path.data_root
    else:
        for field in fields(expected_info):
            actual = getattr(path, field.name)
            expected = getattr(expected_info, field.name)
            assert actual == expected, field.name


def test_inherit_from_existing_path():
    p1 = Path(
        make_path(
            "visitor",
            "ma6658",
            "id21",
            "20250509",
            "RAW_DATA",
            "foo",
            "foo_bar",
            "foo_bar.h5",
        )
    )
    p2 = Path(p1)
    assert p2.esrf_info == p1.esrf_info


def test_parent():
    path = Path(
        make_path(
            "visitor",
            "ma6658",
            "id21",
            "20250509",
            "raw",
            "foo",
            "foo_bar",
            "foo_bar.h5",
        )
    )

    parent = path.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent.esrf_info == path.esrf_info

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent.esrf_info == ESRFv2Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection="foo",
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent.esrf_info == ESRFv2Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection=None,
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent.esrf_info == ESRFv1Info(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        collection=None,
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent.esrf_info is None


def test_str():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = Path(path_str)
    assert str(path) == path_str


def test_repr():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = Path(path_str)
    assert safe_repr(path) == f"ESRFPath('{path_str}')"


def test_dir():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = Path(path_str)
    expected = {field.name for field in fields(ESRFv2Info)}
    assert expected.issubset(set(dir(path)))
