# -*- coding: utf-8 -*-
# mypy: disable-error-code="index"

"""
Datastructure wrappers
"""

import copy

import json

from . import commons
from . import cache


_SINGLETON_CACHES: dict[str, cache.ParsingCache] = {
    commons.DOT: cache.ParsingCache(separator=commons.DOT),
}


def ensure_dict_or_list(
    candidate: commons.ValueType,
    error_message="End point seems to be a leaf instead of a CollectionType instance",
) -> dict | list:
    """Helper fuction making sure the camdidate is a dict or list"""
    if isinstance(candidate, (dict, list)):
        return candidate
    #
    raise TypeError(error_message)


class Structure:
    """A data structure, immutable by default, ..."""

    def __init__(
        self,
        data: commons.ValueType,
        separator: str = commons.DOT,
    ) -> None:
        """Always store a deep copy of data"""
        self.__data = copy.deepcopy(data)
        try:
            self.__cache: cache.ParsingCache = _SINGLETON_CACHES[separator]
        except KeyError:
            self.__cache = _SINGLETON_CACHES.setdefault(
                separator, cache.ParsingCache(separator=separator)
            )
        #

    @property
    def parsing_cache(self) -> cache.ParsingCache:
        """access to the internal cache"""
        return self.__cache

    @property
    def is_mutable(self) -> bool:
        """Return True only from on mutable subclasses"""
        return False

    @property
    def data(self) -> commons.ValueType:
        """access to data"""
        return self.get(())

    def __getitem__(self, full_path: commons.IndexType) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        return self.get(full_path)

    def __get_substructure(self, segments: commons.SegmentsTuple) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        if segments:
            substructure = commons.full_traverse(self.__data, segments)
        else:
            substructure = self.__data
        #
        if self.is_mutable:
            return substructure
        #
        return copy.deepcopy(substructure)

    def get(self, full_path: commons.IndexType) -> commons.ValueType:
        """Return the substructure determined by full_path"""
        return self.__get_substructure(self.__cache[full_path])

    @classmethod
    def from_json_string(cls, json_string: str, separator: str = commons.DOT):
        """Create a new instance from a JSON string"""
        return cls(json.loads(json_string), separator=separator)


class MutableStructure(Structure):
    """A mutable data structure, immutable by default, ..."""

    def __init__(
        self,
        data: commons.ValueType,
        separator: str = commons.DOT,
    ) -> None:
        """Store the data as-is"""
        super().__init__(data, separator=separator)
        self.__mutable = True

    @property
    def is_mutable(self) -> bool:
        """Return True on mutable instances"""
        return self.__mutable

    def freeze(self) -> list[str]:
        """Make the instance immutable and return a list of strings
        describing the effects for debugging purposes
        """
        class_name = self.__class__.__name__
        if self.is_mutable:
            self.__mutable = False
            return [
                f"{class_name} instance changed to immutable",
                "the .get() method will from now on"
                " return a deep copy of the found substructure",
            ]
        #
        return [f"No change, {class_name} instance had already been immutable"]

    def __setitem__(self, full_path: str, new_value: commons.ValueType) -> None:
        """Store a new value. Build the intermediate structure if required."""
        self.update(full_path, new_value, fail_on_missing_keys=False)

    def __delitem__(self, full_path: str) -> None:
        """Delete the specified substructure"""
        self.delete(full_path)

    def __collection_and_key(
        self,
        full_path: commons.IndexType,
    ) -> tuple[commons.ValueType, commons.ValueType]:
        """Return the collection at the last but one path segment,
        and the key determined by the last segment
        """
        segments = self.parsing_cache[full_path]
        if len(segments) < 1:
            raise IndexError(
                f"Minimum one path component is required, but got only {segments!r}"
            )
        #
        partial_traversal_path = segments[:-1]
        return ensure_dict_or_list(
            commons.full_traverse(self.data, partial_traversal_path)
        ), segments[-1]

    def delete(self, full_path: commons.IndexType) -> None:
        """Delete the substructure at full_path"""
        subcollection, key = self.__collection_and_key(full_path)
        del ensure_dict_or_list(subcollection)[key]  # type: ignore[arg-type]

    def update(
        self,
        full_path: commons.IndexType,
        new_value: commons.ValueType,
        fail_on_missing_keys: bool = False,
    ) -> None:
        """Modify the data structure in place setting self[full_path] to new_value"""
        if fail_on_missing_keys:
            # shortcut: regard the full path only
            subcollection, key = self.__collection_and_key(full_path)
        else:
            # slow traversal - search the existing path part,
            # and build a new substructure
            # so in the resulting structure there will be the full path available
            segments = self.parsing_cache[full_path]
            if not segments:
                raise ValueError("Cannot modify with an empty path")
            #
            subcollection, remaining_segments = commons.partial_traverse(
                self.data,
                segments,
                min_remaining_segments=1,
                fail_on_missing_keys=False,
            )
            if len(remaining_segments) > 1:
                # build intermediate path
                still_remaining_segments = list(remaining_segments)
                while len(still_remaining_segments) > 1:
                    key = still_remaining_segments.pop(0)
                    subcollection[key] = {}
                    subcollection = subcollection[key]
                #
                key = still_remaining_segments.pop(0)
                assert not still_remaining_segments
            else:
                key = remaining_segments[0]
            #
        #
        ensure_dict_or_list(subcollection)[key] = new_value  # type: ignore[index]


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
