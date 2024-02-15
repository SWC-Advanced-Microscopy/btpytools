"""
Unit tests to check that imports from brainreg work
These tests are added to deal with this GitHub issue:
https://github.com/SWC-Advanced-Microscopy/btpytools/issues/16

Run with "pytest tests/test_unit/test_brainreg_imports.py" from project root
or simply run pytest to run all tests
"""


import unittest


class TestTransferToServer(unittest.TestCase):
    """
    Run tests associated with btpytools.transferToServer.
    Some functions within this module are hard to understand without the tests
    """

    def test_import_brainreg_core_paths_Paths(self):
        """
        Confirm that import works
        """

        try:
            from brainreg.core.paths import Paths

            print(Paths)  # To avoid errors from flake8
        except ModuleNotFoundError:
            assert False, "Failed to import module brainreg.core.paths.Paths"

    def test_import_brainreg_main(self):
        """
        Confirm that import works
        """

        try:
            from brainreg.core import main

            print(main)
        except ModuleNotFoundError:
            assert False, "Failed to import module brainreg.core.main"

    def test_import_brainreg_cli(self):
        """
        Confirm that import works
        """

        try:
            from brainreg.core import cli

            print(cli)
        except ModuleNotFoundError:
            assert False, "Failed to import module brainreg.core.cli"
