#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import random

from typing import Generic, Union, Mapping


ParameterizedMapping = Mapping[str, int]


@pytest.fixture
def value():
    return {k: random.randint(0, 26) for k in "abc"}


def test_subclass_of_mapping():
    issubclass(ParameterizedMapping, Mapping)


def test_instance_of_mapping(value: ParameterizedMapping):
    assert isinstance(value, Mapping)


def test_instance_of_origin(value: ParameterizedMapping):
    assert isinstance(value, ParameterizedMapping.__origin__)


@pytest.mark.parametrize(
    'i, t', [
        pytest.param(
            i, t, id='__arg__[i]'.format(i)
        ) for i, t in enumerate(
            ParameterizedMapping.__args__
        )
    ]
)
def test_instance_of_args(value: ParameterizedMapping, i: int, t: type):

    if i == 0:
        assert all(isinstance(v, t) for v in value.keys())
    elif i == 1:
        assert all(isinstance(v, t) for v in value.values())
    else:
        raise ValueError("__args__ should have len of 2 for mapping")
