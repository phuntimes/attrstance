#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr
import pytest
import random


from attrstance import InstanceOf, instance_of


def uniform_complex(a: complex, b: complex):
    x = random.uniform(a.real, b.real)
    y = random.uniform(a.imag, b.imag)
    return complex(x, y)


@pytest.fixture
def is_int():
    return instance_of(int)


@pytest.fixture
def is_float():
    return instance_of(float)


@pytest.fixture
def is_string():
    return instance_of(str)


def test_ints(is_int):

    @attr.s
    class Point:
        x = attr.ib(validator=is_int)
        y = attr.ib(validator=is_int)

    x = random.randint(-180, 180)
    y = random.randint(-180, 180)
    new = Point(x, y)


def test_floats(is_float):

    @attr.s
    class Point:
        x = attr.ib(validator=is_float)
        y = attr.ib(validator=is_float)

    x = random.uniform(-180, 180)
    y = random.uniform(-180, 180)
    new = Point(x, y)
