#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr

from attr import Attribute
from typing import Any, Type, Iterable, Iterator, FrozenSet, Callable, NoReturn


Validator = Callable[[Any, Attribute, Any], NoReturn]


def oxford_comma(*args: Any) -> Iterator[str]:
    """
    Generator for representation of all items in the whitelist.
    Follows oxford-comma rules based on length of whitelist.

     - "{!r}" if len(...) == 1
     - "{!r} or {!r}" if len(...) == 2
     - "{!r}, ..., or {!r}" if len(...) > 2

    :param args: collection items
    :return: iterable of reprs
    """
    n = 1 if len(args) > 1 else 0
    for i, t in enumerate(args, n):
        yield "{!r}" if i < len(args) else "or {!r}"


def error_message(*args: Any) -> str:
    """
    Generate an un-formatted error message like:

    `'{name:s}' {constraint:s} {!r}, {!r}, or {!r} ({tobe:s} {value!r}
    that is {actual!r})"`

    Which can then be formatted with error context:

    `'x' must be <class 'str'>, <class 'int'>, or <class 'bytes'>
    (is True that is <class 'bool'>)"`

    :param args: collection items
    :return: un-formatted message
    """
    j = oxford_comma(*args)
    m = "'{{name:s}}' {{constraint:s}} {:s} ({{compliment:s}} " \
        "{{value!r}} that is {{actual!r}})".format(j)
    return m


def format_message(a: Attribute, s: str, v: Any, c: str, *t: Type) -> str:
    """
    Format error message like:

    `'x' must be <class 'str'>, <class 'int'>, or <class 'bytes'>
    (is True that is <class 'bool'>)"`

    from an un-formatted error message like:

    `'{name:s}' {constraint:s} {!r}, {!r}, or {!r} ({tobe:s} {value!r}
    that is {actual!r})"`

    :param a: attribute instance
    :param s: subject complement (i.e. is, has, etc.)
    :param v: passed value
    :param c: constraint detail
    :param t: expected types
    :return: formatted message
    """
    m = error_message(*t)
    m = m.format(
        *t, name=a.name, constraint=c,
        compliment=s, value=v, actual=type(v)
    )
    return m


@attr.s(frozen=True, slots=True)
class TypeValidator(Validator):
    """
    An abstract validator for an :class:`Attribute` of that compares against
    a whitelist of types. The design principle of this validator is that, once
    initialized, the whitelist is immutable and irreplaceable.

    :cvar whitelist: frozenset of types
    """

    whitelist: FrozenSet[Type] = attr.ib()

    @whitelist.validator
    def is_frozenset(self, a: Attribute, v: Any) -> NoReturn:
        """
        Validate that passed value is a frozen set. Note that this is almost
        identical to `instance_of(frozenset)`, but its put here explicitly to
        reduce dependency on :mod:`attr.validators`.

        :param a: attribute instance
        :param v: value passed
        :raise TypeError: if not instance
        """
        if not isinstance(v, frozenset):
            m = format_message(
                a, "is", v,
                "must be", frozenset
            )
            raise TypeError(m, a, v)

    @whitelist.validator
    def not_empty(self, a: Attribute, v: FrozenSet[Any]) -> NoReturn:
        """
        Validate that the passed value is not empty. Due to method ordering,
        validator assumes that :meth:`.is_frozenset` passes.

        :param a: attribute instance
        :param v: value passed
        :raise ValueError: if not populated
        """
        if not len(v) > 0:
            m = format_message(
                a, "is", v,
                "must be non-empty", frozenset
            )
            raise TypeError(m, a, v)

    @whitelist.validator
    def only_types(self, a: Attribute, v: FrozenSet[Any]) -> NoReturn:
        """
        Validate that all items in passed value are types. Due to method
        ordering, validator assumes that :meth:`.is_frozenset` passes.

        :param a: attribute instance
        :param v: value passed
        :raise TypeError: if an entry is not a type
        """
        for x in v:
            if not isinstance(x, type):
                m = format_message(
                    a, "has", x,
                    "must contain", type
                )
                raise TypeError(m, a, x)


@attr.s(frozen=True, slots=True)
class InstanceOf(TypeValidator):
    """
    A validator for an :class:`Attribute` to verify that the passed value is
    a instance (in the contravariant sense) of some class in the whitelist.
    """

    def is_instance(self, v: Any) -> Iterator[bool]:
        """
        Generator function for :func:`isinstance` on the whitelist.

        :return: iterable of bool
        """
        for t in self.whitelist:
            yield isinstance(v, t)

    def __call__(self, i: Any, a: Attribute, v: Any) -> NoReturn:
        """
        Validate that every entry of a passed iterable is an i.

        :param i: dataclass instance
        :param a: attribute instance
        :param v: passed value
        :raise TypeError: if not any i
        """
        if not any(self.is_instance(v)):
            m = format_message(
                a, "is", v,
                "must be", *self.whitelist
            )
            raise TypeError(m, a, self.whitelist, v)


def instance_of(*args: Type):
    """
    A validator for an :class:`Attribute` to verify that the passed value is
    a instance (in the contravariant sense) of some class in the whitelist.

    :param args: whitelist of types
    :return: validator instance
    :raises ValueError: if no whitelist specified
    :raises TypeError: if not all of whitelist are types
    """
    return InstanceOf(frozenset(args))


@attr.s(frozen=True, slots=True)
class SubclassOf(TypeValidator):
    """
    A validator for an :class:`Attribute` to verify that the passed value is
    a subclass (in the contravariant sense) of some class in the whitelist.
    """

    def is_subclass(self, v: Type) -> Iterator[bool]:
        """
        Generator function for :func:`issubclass` on the whitelist.

        :param v: passed value
        :return: iterable of bool
        :raises TypeError: if v is not a type (whitelist pre-validated)
        """
        for c in self.whitelist:
            yield issubclass(v, c)

    def __call__(self, c: Any, a: Attribute, v: Any) -> NoReturn:
        """
        Validate that every entry of a passed iterable is an instance.

        :param c: dataclass instance
        :param a: a instance
        :param v: passed value
        :raise TypeError: if not iterable or any entry is not instance
        """
        try:
            t = any(self.is_subclass(v))

        except TypeError:
            m = format_message(
                a, "is", v,
                "must be", type
            )
            raise TypeError(m, a, v)

        if not t:
            m = format_message(
                a, "is", v,
                "must be a subclass of", *self.whitelist
            )
            raise TypeError(m, a, self.whitelist, v)


def subclass_of(*args: Type):
    """
    A validator for an :class:`Attribute` to verify that the passed value is
    a subclass (in the contravariant sense) of some class in the whitelist..

    :param args: whitelist of types
    :return: validator instance
    :raises ValueError: if no whitelist specified
    :raises TypeError: if not all of whitelist are types
    """
    return SubclassOf(frozenset(args))


@attr.s(frozen=True, slots=True)
class AllInstanceOf(InstanceOf):
    """
    A validator for an :class:`Attribute` of an iterable passed value to
    verify that all elements are an instance (in the contravariant) of some
    type in the whitelist.
    """

    def __call__(self, c: Any, a: Attribute, v: Any) -> NoReturn:
        """
        Validate that every entry of a passed iterable is an instance.

        :param c: dataclass instance
        :param a: attribute instance
        :param v: passed value
        :raise TypeError: if not iterable or any entry is not instance
        """
        try:
            g = iter(v)

        except TypeError:
            m = format_message(
                a, "is", v,
                "must be", Iterable
            )
            raise TypeError(m, a, v)

        for x in g:

            if not self.is_instance(x):
                m = format_message(
                    a, "has", x,
                    "must contain", *self.whitelist
                )
                raise TypeError(m, a, self.whitelist, v)


def all_instance_of(*args: Type):
    """
    A validator for an :class:`Attribute` of an iterable passed value to
    verify that all elements are an instance (in the contravariant) of some
    type in the whitelist.

    :param args: whitelist of types
    :return: validator instance
    :raises ValueError: if no whitelist specified
    :raises TypeError: if not all of whitelist are types
    """
    return AllInstanceOf(frozenset(args))


@attr.s(frozen=True, slots=True)
class AllSubclassOf(SubclassOf):
    """
    A validator for an :class:`Attribute` of an iterable passed value to
    verify that all elements are a subclass (in the contravariant) of some
    type in the whitelist.
    """

    def __call__(self, c: Any, a: Attribute, v: Any) -> NoReturn:
        """
        Validate that every entry of a passed iterable is an instance.

        :param c: dataclass instance
        :param a: attribute instance
        :param v: passed value
        :raise TypeError: if not iterable or any entry is not instance
        """
        try:
            g = iter(v)

        except TypeError:
            m = self.format_message(
                a, "is", v,
                "must be", Iterable
            )
            raise TypeError(m, a, v)

        for x in g:

            try:
                t = any(self.is_subclass(x))

            except TypeError:
                m = self.format_message(
                    a, "has", x,
                    "must contain", type
                )
                raise TypeError(m, a, v)

            if not t:
                m = self.format_message(
                    a, "has", x,
                    "must contain subclass of", *self.whitelist
                )
                raise TypeError(m, a, self.whitelist, v)


def all_subclass_of(*args: Type):
    """
    A validator for an :class:`Attribute` of an iterable passed value to
    verify that all elements are a subclass (in the contravariant) of some
    type in the whitelist.

    :param args: whitelist of types
    :return: validator instance
    :raises ValueError: if no whitelist specified
    :raises TypeError: if not all of whitelist are types
    """
    return SubclassOf(frozenset(args))
