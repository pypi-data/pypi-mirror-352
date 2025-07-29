# -*- coding: utf-8 -*-

"""
common type aliases and constants
"""

from typing import TypeAlias


ScalarType: TypeAlias = str | int | float | bool | None
CollectionType: TypeAlias = dict | list
ValueType: TypeAlias = ScalarType | CollectionType

SegmentsTuple: TypeAlias = tuple[ScalarType, ...]
IndexType: TypeAlias = str | SegmentsTuple


COMMA_BLANK = ", "
DOT = "."
EMPTY = ""
DOUBLE_QUOTE = '"'
SLASH = "/"


def partial_traverse(
    start: ValueType,
    segments: SegmentsTuple,
    min_remaining_segments: int = 0,
    fail_on_missing_keys: bool = True,
) -> tuple[ValueType, SegmentsTuple]:
    """Traverse through a branch starting at the start node,
    until minimum min_remaining_segments of the path are left
    """
    if min_remaining_segments < 0:
        raise ValueError("No negative value allowed here")
    #
    pointer = start
    remaining_segments = list(segments)
    while len(remaining_segments) > min_remaining_segments:
        key = remaining_segments.pop(0)
        if isinstance(pointer, (dict, list)):
            try:
                pointer = pointer[key]  # type: ignore[index]
            except (IndexError, KeyError) as error:
                if fail_on_missing_keys:
                    raise error from error
                #
                return pointer, (key, *remaining_segments)
            #
        else:
            raise TypeError(f"Cannot walk through {pointer!r} using {key!r}")
        #
    #
    return pointer, tuple(remaining_segments)


def full_traverse(
    start: ValueType,
    segments: SegmentsTuple,
) -> ValueType:
    """Traverse through a branch starting at the start node"""
    return partial_traverse(
        start,
        segments,
        min_remaining_segments=0,
        fail_on_missing_keys=True,
    )[0]


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
