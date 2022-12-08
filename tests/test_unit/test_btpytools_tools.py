"""
Unit tests for btpytools.tools
Run with "pytest tests/test_unit/test_btpytools_tools.py" from project root
or simply run pytest to run all tests
"""


import unittest
import os
from os.path import join
from btpytools import tools
from btpytools_test import btpytools_test


class TestTools(unittest.TestCase, btpytools_test):
    """
    Run tests associated with btpytools.tools
    """

    def test_valid_directory_is_valid(self):
        """
        Confirm that folder defined by VALID_SAMPLE_DIR1 is indeed a valid data folder
        """
        self.assertTrue(tools.is_data_folder(self.VALID_SAMPLE_DIR1))
        self.assertTrue(tools.is_data_folder(join(self.CROPPED_ACQ_DIR1, "dir2")))

    def test_has_raw_data(self):
        """
        Confirm that VALID_SAMPLE_DIR1 contains a raw data folder
        """
        self.assertTrue(tools.has_raw_data(self.VALID_SAMPLE_DIR1))

    def test_has_compressed_raw_data(self):
        """
        Confirm that VALID_SAMPLE_DIR1 contains a compressed data folder
        """
        self.assertTrue(tools.has_compressed_raw_data(self.VALID_SAMPLE_DIR1))

    def test_has_recipe_file(self):
        """
        Confirm that VALID_SAMPLE_DIR1 contains a recipe file
        """
        self.assertTrue(tools.has_recipe_file(self.VALID_SAMPLE_DIR1))

    def test_has_scan_settings(self):
        """
        Confirm that VALID_SAMPLE_DIR1 has a scan settings file
        """
        self.assertTrue(tools.has_scan_settings(self.VALID_SAMPLE_DIR1))

    def test_has_stitched_images_directory(self):
        """
        Confirm that VALID_SAMPLE_DIR1 has a stitched images directory
        """
        self.assertTrue(tools.has_stitched_images_directory(self.VALID_SAMPLE_DIR1))

    def test_has_no_stitched_images_directory(self):
        """
        Confirm that VALID_SAMPLE_DIR2 has no stitched images directory
        """
        self.assertFalse(tools.has_stitched_images_directory(self.VALID_SAMPLE_DIR2))

    def test_uncropped_stitched_images(self):
        """
        Confirm that VALID_SAMPLE_DIR1 has an uncropped data directory
        """
        self.assertTrue(tools.has_uncropped_stitched_images(self.VALID_SAMPLE_DIR1))

    def test_invalid_directories_are_invalid(self):
        """
        Confirm that invalid directories are, indeed, invalid
        """
        invalid_dir = join(self.DATA_DIR, "invalid_data_dirs")

        for t_path in os.listdir(invalid_dir):
            self.assertFalse(tools.is_data_folder(join(invalid_dir, t_path)))

    def test_contains_data_subfolders(self):
        """
        Confirm that folder contains sub-folders that are data folders
        """
        self.assertTrue(tools.contains_data_folders(self.CROPPED_ACQ_DIR1))

    def test_contains_two_downsampled_dirs(self):
        """
        Confirm that the downsampled stacks directory in the valid sample has four downsampled
        stacks: two channels by two resolutions
        """
        out = tools.available_downsampled_volumes(
            self.VALID_SAMPLE_DIR1, verbose=True
        )
        self.assertTrue(len(out) == 4)
