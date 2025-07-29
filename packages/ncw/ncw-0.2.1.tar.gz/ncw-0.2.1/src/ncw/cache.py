# -*- coding: utf-8 -*-

"""
ParsingCache
"""

import json
import re

from collections import Counter
from threading import Lock

from . import commons


NEXT_QUOTED = re.compile('^"([^"]+)"')
NEXT_IN_SUBSCRIPT_QUOTED = re.compile(r'^\["([^"]+)"\]')
NEXT_IN_SUBSCRIPT_SIMPLE = re.compile(r"^\[([^\]]+)\]")


class ParsingCache:
    """Can build a tuple of segments from a string"""

    def __init__(self, separator: str = commons.DOT) -> None:
        """..."""
        self.__separator = separator
        self._active = False
        self._expect_segment_end = False
        self._collected_segments: list[commons.ScalarType] = []
        self._current_segment_sources: list[str] = []
        self.__cache: dict[str, commons.SegmentsTuple] = {}
        self.stats: Counter[str] = Counter()
        self.__lock = Lock()

    @property
    def separator(self) -> str:
        """Return the separator string"""
        return self.__separator

    def __getitem__(self, key: commons.IndexType) -> commons.SegmentsTuple:
        """Return an item from the cache if the key is a string"""
        if isinstance(key, str):
            return self.get_cached(key)
        #
        self.stats.update(bypass=1)
        return key

    def get_cached(self, key: str) -> commons.SegmentsTuple:
        """Return an item from the cache"""
        if not key:
            self.stats.update(bypass=1)
            return ()
        #
        with self.__lock:
            stat_entries = []
            try:
                cached_segments = self.__cache[key]
            except KeyError:
                cached_segments = self.__cache.setdefault(
                    key, self.split_into_segments(key)
                )
                stat_entries.append("miss")
            else:
                stat_entries.append("hit")
            #
            self.stats.update(stat_entries)
            return cached_segments
        #

    def canonical(self, source_segments: commons.SegmentsTuple) -> str:
        """Return the canonical source for the given segments tuple"""
        output: list[str] = []
        for item in source_segments:
            if isinstance(item, str) and not any(
                char in item for char in (self.separator, commons.DOUBLE_QUOTE, "[")
            ):
                output.append(item)
            else:
                output.append(json.dumps(item))
            #
        #
        reconstructed_key = self.separator.join(output)
        cached_segments = self.__cache.setdefault(reconstructed_key, source_segments)
        if cached_segments != source_segments:
            # XXX: should never occur
            raise ValueError("Canonical representation mismatch")
        #
        return reconstructed_key

    def add_segment(self, segment_source: str) -> None:
        """Add a new segment from segment_source"""
        try:
            segment = json.loads(segment_source)
        except json.JSONDecodeError:
            segment = segment_source
        #
        self._collected_segments.append(segment)
        self._current_segment_sources.clear()

    def store_and_reset_segment(self) -> None:
        """reset the internal state between segments"""
        if self._current_segment_sources:
            self.add_segment(commons.EMPTY.join(self._current_segment_sources))
        #
        self._expect_segment_end = False

    def add_match_and_get_end_pos(self, match: re.Match, quote: bool = False) -> int:
        """Add the matched portion that is quoted or in a subscript ([...])
        and return the match end position
        """
        self._expect_segment_end = True
        segment_source = f'"{match.group(1)}"' if quote else match.group(1)
        self.add_segment(segment_source)
        return match.end()

    def check_for_fast_forward(self, path_source: str, pos: int) -> int:
        """Check if we can fast-forward"""
        if self._current_segment_sources:
            return 0
        #
        remainder = path_source[pos:]
        character = remainder[0]
        if character == commons.DOUBLE_QUOTE:
            match = NEXT_QUOTED.match(remainder)
            if match:
                return self.add_match_and_get_end_pos(match, quote=True)
            #
        elif character == "[":
            quote = True
            match = NEXT_IN_SUBSCRIPT_QUOTED.match(remainder)
            if not match:
                quote = False
                match = NEXT_IN_SUBSCRIPT_SIMPLE.match(remainder)
            #
            if match:
                return self.add_match_and_get_end_pos(match, quote=quote)
            #
        #
        return 0

    def split_into_segments(self, path_source: str) -> commons.SegmentsTuple:
        """Split a string into a tuple of segments suitable
        for instantiating a TraversalPath object
        """
        if self._active:
            raise ValueError(
                f"{self.__class__.__name__} instances are not thread-safe,"
                " concurrent execution on the same instance is not supported."
            )
        #
        self._active = True
        self.store_and_reset_segment()
        self._collected_segments.clear()
        pos = 0
        path_source_length = len(path_source)
        while pos < path_source_length:
            character = path_source[pos]
            if character == self.separator:
                self.store_and_reset_segment()
                pos += 1
                continue
            #
            if self._expect_segment_end:
                raise ValueError(
                    f"Expected segment end but read character {character!r}."
                    f" Collected segments so far: {self._collected_segments!r}"
                )
            #
            fast_forward = self.check_for_fast_forward(path_source, pos)
            if fast_forward:
                pos += fast_forward
            else:
                self._current_segment_sources.append(character)
                pos += 1
            #
        #
        self.store_and_reset_segment()
        found_segments = tuple(self._collected_segments)
        self._collected_segments.clear()
        self._active = False
        return found_segments


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
