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
VALID_SAMPLE_DIR1 = join(DATA_DIR, "valid_sample_directory_01")
VALID_SAMPLE_DIR2 = join(DATA_DIR, "valid_sample_directory_02")
CROPPED_ACQ_DIR1 = join(DATA_DIR, "contains_data_subfolders_01")
CROPPED_ACQ_DIR2 = join(DATA_DIR, "contains_data_subfolders_02")


class TestTools(unittest.TestCase):
    """
    Run tests associated with btpytools.tools
    """

    def test_valid_directory_is_valid(self):
        """
        Confirm if folder defined by VALID_SAMPLE_DIR1 is indeed valid
        """
        self.assertTrue(tools.is_data_folder(VALID_SAMPLE_DIR1))

    def test_has_raw_data(self):
        """
        Confirm if VALID_SAMPLE_DIR1 contains a raw data folder
        """
        self.assertTrue(tools.has_raw_data(VALID_SAMPLE_DIR1))

    def test_has_compressed_raw_data(self):
        """
        Confirm if VALID_SAMPLE_DIR1 contains a compressed data folder
        """
        self.assertTrue(tools.has_compressed_raw_data(VALID_SAMPLE_DIR1))

    def test_has_recipe_file(self):
        """
        Confirm if VALID_SAMPLE_DIR1 contains a recipe file
        """
        self.assertTrue(tools.has_recipe_file(VALID_SAMPLE_DIR1))

    def test_has_scan_settings(self):
        """
        Confirm if VALID_SAMPLE_DIR1 has a scan settings file
        """
        self.assertTrue(tools.has_scan_settings(VALID_SAMPLE_DIR1))

    def test_has_stitched_images_directory(self):
        """
        Confirm if VALID_SAMPLE_DIR1 has a stitched images directory
        """
        self.assertTrue(tools.has_stitched_images_directory(VALID_SAMPLE_DIR1))

    def test_uncropped_stitched_images(self):
        """
        Confirm if VALID_SAMPLE_DIR1 has an uncropped data directory
        """
        self.assertTrue(tools.has_uncropped_stitched_images(CROPPED_ACQ_DIR1))

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
        self.assertTrue(tools.contains_data_folders(CROPPED_ACQ_DIR1))

    def test_contains_two_downsampled_dirs(self):
        """
        Confirm that the downsampled stacks directory in the valid sample has two downsampled
        stacks
        """
        out = tools.available_downsampled_volumes(VALID_SAMPLE_DIR1, verbose=True)
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

    def test_user_specified_two_individual_dirs(self):
        """
        User specifies two cropped samples within a single acquisition
        """
        t_dirs = [join(CROPPED_ACQ_DIR1, "dir1"), join(CROPPED_ACQ_DIR1, "dir1")]
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_dirs))

    def test_user_specifies_valid_directories(self):
        """
        Should return False because this is not a cropped sample
        """
        self.assertFalse(
            tts.user_specified_cropped_directories_individually(VALID_SAMPLE_DIR1)
        )

        self.assertFalse(
            tts.user_specified_cropped_directories_individually(
                [VALID_SAMPLE_DIR1, VALID_SAMPLE_DIR2]
            )
        )

    def test_user_mixes_individual_and_single_valid(self):
        """
        The user mixes indiviudally specified directories with "valid" samples directories.
        We should return true
        """
        t_dirs = [join(CROPPED_ACQ_DIR1, "dir1"), join(CROPPED_ACQ_DIR1, "dir1")]

        # With one valid sample directory at the list end
        t_1 = t_dirs
        t_1.append(VALID_SAMPLE_DIR1)
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_1))

        # With one valid sample directory at the list start
        t_2 = t_dirs
        t_2.insert(0, VALID_SAMPLE_DIR1)
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_2))

    def test_user_specifies_one_directory_from_a_cropped_acq(self):
        """
        Should return True because this is a cropped sample.
        """
        out = tts.user_specified_cropped_directories_individually(
            join(CROPPED_ACQ_DIR1, "dir1")
        )
        self.assertTrue(out)

    def test_identify_missed_raw_data_archive(self):
        """
        Check whether, we correctly identify a list of source directories as being problematic
        for not having raw data being sent.
        """
        f_1 = [join(CROPPED_ACQ_DIR1, "dir1"), join(CROPPED_ACQ_DIR1, "dir2")]
        self.assertTrue(tts.issue_warning_if_compressed_data_will_not_be_sent(f_1))

    def test_identify_acceptable_individually_specified_dirs(self):
        """
        Check whether directories specified individually are are nontheless OK
        """

        # Should pass because user supplies compressed archive
        t_1 = [
            join(CROPPED_ACQ_DIR1, "dir1"),
            join(CROPPED_ACQ_DIR1, "dir2"),
            join(CROPPED_ACQ_DIR1, "compressed_rawData.tar.bz"),
        ]

        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_1))

        # Should pass because specified dirs are in a directory with no compressed data
        crop_no_comp_dat = join(DATA_DIR, "contains_data_subfolders_no_compress_data")
        t_2 = [join(crop_no_comp_dat, "dir1"), join(crop_no_comp_dat, "dir2")]
        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_2))

    def test_compressed_data_warning_with_normal_call_structure(self):
        """
        Test whether a normal call structure (e.g. a cropped roor dir) will trigger no error
        """

        self.assertFalse(
            tts.issue_warning_if_compressed_data_will_not_be_sent(VALID_SAMPLE_DIR1)
        )
        self.assertFalse(
            tts.issue_warning_if_compressed_data_will_not_be_sent(CROPPED_ACQ_DIR1)
        )

        # Two directories containing cropped acquisitions should also pass
        t_1 = [CROPPED_ACQ_DIR1, CROPPED_ACQ_DIR2]
        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_1))

    def test_identify_peculiar_individually_specified_cases(self):
        """
        The user might mix and match individually specified directories with "normal" directories.
        Check these cases: when in doubt we just want to flag it.
        """
        f_1 = [
            join(CROPPED_ACQ_DIR1, "dir1"),
            join(CROPPED_ACQ_DIR1, "dir2"),
            VALID_SAMPLE_DIR1,
        ]

        f_2 = [
            VALID_SAMPLE_DIR1,
            join(CROPPED_ACQ_DIR1, "dir1"),
            join(CROPPED_ACQ_DIR1, "dir2"),
        ]
        self.assertTrue(tts.issue_warning_if_compressed_data_will_not_be_sent(f_1))
        self.assertTrue(
            tts.issue_warning_if_compressed_data_will_not_be_sent(f_2, verbose=True)
        )
