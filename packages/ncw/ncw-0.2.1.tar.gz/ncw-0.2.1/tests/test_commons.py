"""test_ncw"""

from ncw import commons

from . import test_base as tb


class PartialTraverse(tb.VerboseTestCase):
    """partial_tracerse() function"""

    def test_valid_call(self):
        """call with valid data"""
        # config = json.loads(tb.SIMPLE_TESTDATA)
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.partial_traverse(config, ("metadata", "request", "ref")),
            (config["metadata"]["request"]["ref"], ()),
        )

    def test_through_a_leaf(self):
        """trying to traverse through a leaf"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^Cannot walk through 'issue-12345' using 'sub-item'",
            commons.partial_traverse,
            config,
            ("metadata", "request", "ref", "sub-item"),
        )

    def test_invalid_key(self):
        """trying to use an invalid key"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            KeyError,
            "^'xyz'",
            commons.partial_traverse,
            config,
            ("metadata", "request", "xyz"),
        )

    def test_invalid_key_fail_false(self):
        """trying to use an invalid key"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.partial_traverse(
                config,
                ("metadata", "request", "xyz"),
                fail_on_missing_keys=False,
            ),
            (
                {
                    "ref": "issue-12345",
                    "date": "2025-01-23",
                },
                ("xyz",),
            ),
        )

    def test_through_list_with_invalid_index(self):
        """Call with an indvalid list index"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertRaisesRegex(
            TypeError,
            "^list indices must be integers or slices, not ",
            commons.partial_traverse,
            config,
            ("metadata", "contact", "first"),
        )


class FullTRaverse(tb.VerboseTestCase):
    """full_traverse() function"""

    def test_non_empty(self):
        """non-empty traversal path segments"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(
            commons.full_traverse(config, ("metadata", "contact", 0)),
            "user@example.com",
        )

    def test_full_traverse_empty(self):
        """empty traversal path segmentss"""
        config = tb.load_testdata(tb.SIMPLE)
        self.assertEqual(commons.full_traverse(config, ()), config)
