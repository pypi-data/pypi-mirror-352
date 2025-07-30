"""test the __main__ module"""

import importlib.metadata
import io

from unittest.mock import patch

from ncw import __main__ as ncw_main

from . import test_base as tb


class Main(tb.VerboseTestCase):
    """main() function"""

    # pylint: disable=protected-access ; makes sense in test cases

    @patch("importlib.metadata")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_with_version(self, mock_stdout, mock_metadata):
        """store_and_reset_segment() method"""
        mock_metadata.version.return_value = "1.2.3"
        with patch("sys.argv", new=["ncw", "--version"]):
            self.assertRaises(SystemExit, ncw_main.main)
        #
        self.assertEqual(mock_stdout.getvalue(), "1.2.3\n")
        mock_metadata.version.assert_called_with(ncw_main._PACKAGE_NAME)

    @patch("importlib.metadata.version")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_with_missing_version(self, mock_stdout, mock_metadata_version):
        """store_and_reset_segment() method"""
        mock_metadata_version.side_effect = importlib.metadata.PackageNotFoundError(
            "xyz"
        )
        with patch("sys.argv", new=["ncw", "--version"]):
            self.assertRaises(SystemExit, ncw_main.main)
        #
        self.assertEqual(
            mock_stdout.getvalue(), "No package metadata was found for xyz\n"
        )
        mock_metadata_version.assert_called_with(ncw_main._PACKAGE_NAME)
