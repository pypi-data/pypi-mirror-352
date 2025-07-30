"""ncw.cache module tests"""

import collections
import re

from unittest.mock import call, patch

from ncw import cache

from . import test_base as tb


class SegmentsParser(tb.VerboseTestCase):
    """SegmentsParser class"""

    # pylint: disable=protected-access ; makes sense in test cases

    def test_add_segment(self):
        """add_segment() method"""
        builder = cache.SegmentsParser()
        builder.add_segment("abc")
        builder.add_segment('"xyz"')
        builder.add_segment("1024")
        builder.add_segment("3.141")
        builder.add_segment("true")
        builder.add_segment("null")
        self.assertListEqual(
            builder._collected_segments,
            ["abc", "xyz", 1024, 3.141, True, None],
        )

    @patch.object(cache.SegmentsParser, "add_segment")
    def test_store_and_reset_segment(self, mock_add_segment):
        """store_and_reset_segment() method"""
        builder = cache.SegmentsParser()
        builder._expect_segment_end = True
        builder.store_and_reset_segment()
        self.assertFalse(builder._expect_segment_end)
        builder._current_segment_sources.append("77")
        builder._current_segment_sources.append("99")
        builder.store_and_reset_segment()
        mock_add_segment.assert_called_with("7799")

    @patch.object(cache.SegmentsParser, "add_segment")
    def test_add_match_and_get_end_pos(self, mock_add_segment):
        """add_match_and_get_end_pos() method"""
        builder = cache.SegmentsParser()
        builder._expect_segment_end = False
        match = re.match(".+(remove_this)", "tony@tiremove_thisger.net")
        if match:
            self.assertEqual(
                builder.add_match_and_get_end_pos(match),
                18,
            )
            self.assertTrue(builder._expect_segment_end)
            mock_add_segment.assert_called_with("remove_this")
        #
        match = re.match('^"([^"]+)"', '"quoted".not quoted.[in subscript]"')
        if match:
            self.assertEqual(
                builder.add_match_and_get_end_pos(match, quote=True),
                8,
            )
            self.assertTrue(builder._expect_segment_end)
            mock_add_segment.assert_called_with('"quoted"')
        #

    @patch.object(cache.SegmentsParser, "add_match_and_get_end_pos")
    def test_check_for_fast_forward(self, mock_amagep):
        """check_for_fast_forward() method"""
        builder = cache.SegmentsParser()
        builder._current_segment_sources.append("data")
        path_source = '"quoted".not quoted.[in subscript].["quoted in subscript"]'
        mock_amagep.return_value = 8
        self.assertEqual(
            builder.check_for_fast_forward(path_source, 0),
            0,
        )
        builder._current_segment_sources.clear()
        self.assertEqual(
            builder.check_for_fast_forward(path_source, 0),
            8,
        )
        self.assertEqual(
            builder.check_for_fast_forward(path_source, 9),
            0,
        )
        mock_amagep.return_value = 14
        self.assertEqual(
            builder.check_for_fast_forward(path_source, 20),
            14,
        )
        mock_amagep.return_value = 23
        self.assertEqual(
            builder.check_for_fast_forward(path_source, 35),
            23,
        )
        self.assertEqual(len(mock_amagep.mock_calls), 3)

    def test_split_into_segments(self):
        """split_into_segments() method without mocks"""
        builder = cache.SegmentsParser()
        with self.subTest("faked concurrent execution"):
            builder._active = True
            self.assertRaisesRegex(
                ValueError,
                "SegmentsParser instances are not thread-safe,"
                " concurrent execution on the same instance is not supported.",
                builder.split_into_segments,
                "abc.def.ghi",
            )
        #
        builder._active = False
        for source, expected_results in (
            ("abc.def.ghi", ("abc", "def", "ghi")),
            ('xyz.2."3".[null].true.[7.353]', ("xyz", 2, "3", None, True, 7.353)),
        ):
            with self.subTest(
                "success", source=source, expected_results=expected_results
            ):
                self.assertTupleEqual(
                    builder.split_into_segments(source), expected_results
                )
            #
        #
        with self.subTest("junk after quoted segment"):
            self.assertRaisesRegex(
                ValueError,
                "Expected segment end but read character 'g'."
                r" Collected segments so far: \['abc', 'def'\]",
                builder.split_into_segments,
                'abc."def"ghi.jkl',
            )
        #


class ParsingCache(tb.VerboseTestCase):
    """ParsingCache class"""

    def test_attributes(self):
        """Initialization and attributes"""
        pc = cache.ParsingCache(separator="/")
        self.assertEqual(pc.separator, "/")
        self.assertEqual(pc.stats, collections.Counter())

    def test_getitem_bypass(self):
        """item access with cache bypass"""
        pc = cache.ParsingCache(separator="/")
        self.assertTupleEqual(pc[1, 2, None, True], (1, 2, None, True))
        self.assertEqual(pc.stats, collections.Counter(bypass=1))

    @patch.object(cache.ParsingCache, "get_cached")
    def test_getitem_cached(self, mock_get_cached):
        """item access through cache"""
        pc = cache.ParsingCache(separator="/")
        mock_get_cached.return_value = (7, 8.23, False)
        self.assertTupleEqual(pc["7/8.23/false"], (7, 8.23, False))
        mock_get_cached.assert_called_with("7/8.23/false")
        self.assertEqual(pc.stats, collections.Counter())

    def test_get_cached_bypass(self):
        """.get_cached() method with empty string"""
        pc = cache.ParsingCache(separator="/")
        self.assertTupleEqual(pc.get_cached(""), ())
        self.assertEqual(pc.stats, collections.Counter(bypass=1))

    @patch.object(cache, "SegmentsParser")
    def test_get_cached_miss(self, mock_sp):
        """.get_cached() method initiallyseting a value in the cache"""
        pc = cache.ParsingCache(separator=",")
        sp_instance = mock_sp()
        sp_instance.split_into_segments.return_value = (1, 2, "many")
        self.assertTupleEqual(pc.get_cached("1,2,many"), (1, 2, "many"))
        sp_instance.split_into_segments.assert_called_with("1,2,many")
        self.assertEqual(pc.stats, collections.Counter(miss=1))

    @patch.object(cache, "SegmentsParser")
    def test_get_cached_hits(self, mock_sp):
        """.get_cached() method setting and retrieving cache items"""
        pc = cache.ParsingCache(separator="|")
        sp_instance = mock_sp()
        sp_instance.split_into_segments.side_effect = [
            (0, 1, "some"),
            (99.3, None),
            ("x", "y"),
        ]
        for path, expected_split in (
            ("0|1|some", (0, 1, "some")),
            ("0|1|some", (0, 1, "some")),
            ("0|1|some", (0, 1, "some")),
            ("99.3|null", (99.3, None)),
            ("99.3|null", (99.3, None)),
        ):
            with self.subTest("hit or miss", path=path, expected_split=expected_split):
                self.assertTupleEqual(pc.get_cached(path), expected_split)
            #
        #
        self.assertListEqual(
            sp_instance.method_calls,
            [
                call.split_into_segments("0|1|some"),
                call.split_into_segments("99.3|null"),
            ],
        )
        self.assertEqual(pc.stats, collections.Counter(miss=2, hit=3))

    def test_canonical(self) -> None:
        """.canonical() method"""
        pc = cache.ParsingCache()
        testdata: list[tuple[cache.commons.SegmentsTuple, str]] = [
            ((0, 1, "some"), "0.1.some"),
            ((67.54, True, None), "[67.54].true.null"),
            (
                ('special "segment"', "differently ][ special"),
                r'"special \"segment\""."differently ][ special"',
            ),
        ]
        for segments, expected_result in testdata:
            with self.subTest(
                "representation", segments=segments, expected_result=expected_result
            ):
                self.assertEqual(pc.canonical(segments), expected_result)
            #
        #
        for expected_segments, path in testdata:
            with self.subTest(
                "hits only", path=path, expected_segments=expected_segments
            ):
                self.assertTupleEqual(pc.get_cached(path), expected_segments)
            #
        #
        self.assertEqual(pc.stats["hit"], 3)
        self.assertEqual(pc.stats["miss"], 0)
