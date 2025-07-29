"""test_ncw"""

import re

from unittest.mock import patch

from ncw import cache

from . import test_base as tb


class ParsingCache(tb.VerboseTestCase):
    """ParsingCache class"""

    # pylint: disable=protected-access ; makes sense in test cases

    def test_add_segment(self):
        """add_segment() method"""
        builder = cache.ParsingCache()
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

    @patch.object(cache.ParsingCache, "add_segment")
    def test_store_and_reset_segment(self, mock_add_segment):
        """store_and_reset_segment() method"""
        builder = cache.ParsingCache()
        builder._expect_segment_end = True
        builder.store_and_reset_segment()
        self.assertFalse(builder._expect_segment_end)
        builder._current_segment_sources.append("77")
        builder._current_segment_sources.append("99")
        builder.store_and_reset_segment()
        mock_add_segment.assert_called_with("7799")

    @patch.object(cache.ParsingCache, "add_segment")
    def test_add_match_and_get_end_pos(self, mock_add_segment):
        """add_match_and_get_end_pos() method"""
        builder = cache.ParsingCache()
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

    @patch.object(cache.ParsingCache, "add_match_and_get_end_pos")
    def test_check_for_fast_forward(self, mock_amagep):
        """check_for_fast_forward() method"""
        builder = cache.ParsingCache()
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
        builder = cache.ParsingCache()
        with self.subTest("faked concurrent execution"):
            builder._active = True
            self.assertRaisesRegex(
                ValueError,
                "ParsingCache instances are not thread-safe,"
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
