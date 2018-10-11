#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import random

from typing import Iterator, Tuple, Union, Mapping
from string import ascii_lowercase as lc


StrOrInt = Union[str, int]
Parameterized = Mapping[StrOrInt, StrOrInt]


def int_int(r: int) -> Iterator[Tuple[int, int]]:
    for i in range(r):
        j = random.randint(0, 25)
        yield i, j


def int_str(r: int) -> Iterator[Tuple[int, str]]:
    for i in range(r):
        j = random.randint(0, 25)
        yield i, lc[j]


def str_int(r: int) -> Iterator[Tuple[str, int]]:
    for i in range(r):
        j = random.randint(0, 25)
        yield lc[i], j


def str_str(r: int) -> Iterator[Tuple[str, str]]:
    for i in range(r):
        j = random.randint(0, 25)
        yield lc[i], lc[j]


def choice(k: int) -> StrOrInt:
    return lc[k] if random.random() < 0.5 else k


def mixed(r: int) -> Iterator[Tuple[StrOrInt, StrOrInt]]:
    for i in range(r):
        j = random.randint(0, 25)
        x, y = map(choice, (i, j))
        yield x, y


@pytest.fixture(
    params=[
        pytest.param(int_int, id="Mapping[int, int]"),
        pytest.param(str_str, id="Mapping[str, str]"),
        pytest.param(int_str, id="Mapping[int, str]"),
        pytest.param(str_int, id="Mapping[str, int]"),
        pytest.param(mixed, id="Mapping[StrOrInt, StrOrInt]"),
    ]
)
def value(request):
    g = request.param
    return dict(g(5))


def test_instance_of_origin(value: Parameterized):
    assert isinstance(value, Parameterized.__origin__)


@pytest.mark.parametrize(
    'i, t', [
        pytest.param(
            i, t, id="__arg__[{:d}]".format(i)
        ) for i, t in enumerate(
            Parameterized.__args__
        )
    ]
)
def test_instance_of_args_only_int(value: Parameterized, i: int, t: Union):

    if i == 0:
        assert all(isinstance(v, t.__args__) for v in value.keys())
    elif i == 1:
        assert all(isinstance(v, t.__args__) for v in value.values())
    else:
        raise ValueError("__args__ should have len of 2 for mapping")
