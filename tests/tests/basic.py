"""
Unit tests for btpytools
Run with "pytest tests/tests/basic.py" from project root
"""


import unittest
import os
from os.path import join
from btpytools import transferToServer as tts
from btpytools import tools


DATA_DIR = join("tests", "data")
VALID_SAMPLE_DIR = join(DATA_DIR, "valid_sample_directory")
CROPPED_ACQ_DIR = join(DATA_DIR, "contains_data_subfolders")


class TestTools(unittest.TestCase):
    """
    Run tests associated with btpytools.tools
    """

    def test_valid_directory_is_valid(self):
        """
        Confirm if folder defined by VALID_SAMPLE_DIR is indeed valid
        """
        self.assertTrue(tools.is_data_folder(VALID_SAMPLE_DIR))

    def test_has_raw_data(self):
        """
        Confirm if VALID_SAMPLE_DIR contains a raw data folder
        """
        self.assertTrue(tools.has_raw_data(VALID_SAMPLE_DIR))

    def test_has_compressed_raw_data(self):
        """
        Confirm if VALID_SAMPLE_DIR contains a compressed data folder
        """
        self.assertTrue(tools.has_compressed_raw_data(VALID_SAMPLE_DIR))

    def test_has_recipe_file(self):
        """
        Confirm if VALID_SAMPLE_DIR contains a recipe file
        """
        self.assertTrue(tools.has_recipe_file(VALID_SAMPLE_DIR))

    def test_has_scan_settings(self):
        """
        Confirm if VALID_SAMPLE_DIR has a scan settings file
        """
        self.assertTrue(tools.has_scan_settings(VALID_SAMPLE_DIR))

    def test_has_stitched_images_directory(self):
        """
        Confirm if VALID_SAMPLE_DIR has a stitched images directory
        """
        self.assertTrue(tools.has_stitched_images_directory(VALID_SAMPLE_DIR))

    def test_uncropped_stitched_images(self):
        """
        Confirm if VALID_SAMPLE_DIR has an uncropped data directory
        """
        self.assertTrue(tools.has_uncropped_stitched_images(CROPPED_ACQ_DIR))

    def test_invalid_directories_are_invalid(self):
        """
        Confirm if that invalid directories are, indeed, invalid
        """
        invalid_dir = join(DATA_DIR, "invalid_data_dirs")

        for t_path in os.listdir(invalid_dir):
            self.assertFalse(tools.is_data_folder(join(invalid_dir, t_path)))

    def test_contains_data_subfolders(self):
        """
        Confirm that folder contains sub-folders that are data folders
        """
        self.assertTrue(tools.contains_data_folders(CROPPED_ACQ_DIR))

    def test_contains_two_downsampled_dirs(self):
        """
        Confirm that the downsampled stacks directory in the valid sample has two downsampled
        stacks
        """
        out = tools.available_downsampled_volumes(VALID_SAMPLE_DIR, verbose=True)
        self.assertTrue(len(out) == 4)


class TestTransferToServer(unittest.TestCase):
    """
    Run tests associated with btpytools.transferToServer.
    Some functions within this module are hard to understand without the tests
    """

    def test_check_directories_exist(self):
        """
        Confirm if that that two data directories exist
        """
        out = tts.check_directories(join(DATA_DIR, "dir_a"), join(DATA_DIR, "dir_b"))
        self.assertTrue(out)

    def test_dir_list_contains_compressed_archive(self):
        """
        Confirm that the list of paths contains at least one compressed archive
        """
        a_1 = ["dir1/dir2/stuff_rawData.tar.bz", "dir_a", "dir_b"]
        a_2 = ["dir1/dir2/stuff_rawData.tar.gz", "dir_a", "dir_b"]
        a_3 = [
            "dir1/dir2/stuff_rawData.tar.gz",
            "dir_a",
            "dir_b",
            "dir1/dir2/stuff_rawData.tar.bz",
        ]
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_1))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_2))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_3))

    def test_dir_list_not_contains_compressed_archive(self):
        """
        Confirm that the list of paths contains no compressed archives
        """
        b_1 = ["dir1/dir2", "dir_a", "dir_b"]
        b_2 = ["dir1/dir2/stuff_rawData.tar", "dir_a", "dir_b"]
        b_3 = ["dir1/dir2/stuff_rawData", "dir_a", "dir_b", "dir1/dir2/rawData"]
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_1))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_2))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_3))

    def test_user_specified_individual_dirs(self):
        """
        User specifies two cropped samples within a single acquisition
        """
        t_dirs = [join(CROPPED_ACQ_DIR, "dir1"), join(CROPPED_ACQ_DIR, "dir1")]
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_dirs))

    def test_user_specifies_one_valid_directory(self):
        """
        Should return False because this is not a cropped sample
        """
        self.assertFalse(
            tts.user_specified_cropped_directories_individually(VALID_SAMPLE_DIR)
        )

    def test_user_specifies_one_directory_from_a_cropped_acq(self):
        """
        Should return True because this is a cropped sample
        """
        out = tts.user_specified_cropped_directories_individually(
            join(CROPPED_ACQ_DIR, "dir1")
        )
        self.assertTrue(out)
