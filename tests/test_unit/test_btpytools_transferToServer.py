"""
Unit tests for btpytools.transferToServer
Run with "pytest tests/test_unit/test_btpytools_transferToServer.py" from project root
or simply run pytest to run all tests
"""


import unittest
from os.path import join, split
from btpytools import transferToServer as tts
from btpytools_test import btpytools_test


class TestTransferToServer(unittest.TestCase, btpytools_test):
    """
    Run tests associated with btpytools.transferToServer.
    Some functions within this module are hard to understand without the tests
    """

    def test_check_directories_exist(self):
        """
        Confirm if that that two data directories exist
        """
        out = tts.check_directories(
            join(self.DATA_DIR, "dir_a"), join(self.DATA_DIR, "dir_b")
        )
        self.assertTrue(out)

    def test_dir_list_contains_compressed_archive(self):
        """
        Confirm that the list of paths contains at least one compressed archive
        """
        a_1 = [join("dir1", "dir2", "stuff_rawData.tar.bz"), "dir_a", "dir_b"]
        a_2 = [join("dir1", "dir2", "stuff_rawData.tar.gz"), "dir_a", "dir_b"]
        a_3 = [
            join("dir1", "dir2", "stuff_rawData.tar.gz"),
            "dir_a",
            "dir_b",
            join("dir1", "dir2", "stuff_rawData.tar.bz"),
        ]
        a_4 = [
            join("tests", "data", "contains_data_subfolders_01", "dir1"),
            join("tests", "data", "contains_data_subfolders_01", "dir1"),
            join(
                "tests",
                "data",
                "contains_data_subfolders_01",
                "compressed_rawData.tar.bz",
            ),
        ]

        self.assertTrue(tts.dir_list_contains_compressed_archive(a_1))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_2))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_3))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a_4))
        self.assertTrue(
            tts.dir_list_contains_compressed_archive(a_4, split(a_4[0])[0])
        )

    def test_dir_list_not_contains_compressed_archive(self):
        """
        Confirm that the list of paths contains no compressed archives
        """
        b_1 = [join("dir1", "dir2"), "dir_a", "dir_b"]
        b_2 = [join("dir1", "dir2", "stuff_rawData.tar"), "dir_a", "dir_b"]
        b_3 = [
            join("dir1", "dir2", "stuff_rawData"),
            "dir_a",
            "dir_b",
            join("dir1", "dir2", "rawData"),
        ]
        # b_4 has a compressed archive but it is in a different path so we want to return false
        b_4 = [
            join("s_dir", "sample1"),
            join("s_dir", "sample2"),
            join("OTHER_DIR", "rawData.tar.bz"),
        ]
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_1))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_2))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_3))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b_4, "s_dir"))

    def test_user_specified_two_individual_dirs(self):
        """
        User specifies two cropped samples within a single acquisition
        """
        t_dirs = [
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir1"),
        ]
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_dirs))

    def test_user_specifies_valid_directories(self):
        """
        Should return False because this is not a cropped sample
        """
        self.assertFalse(
            tts.user_specified_cropped_directories_individually(
                self.VALID_SAMPLE_DIR1
            )
        )

        self.assertFalse(
            tts.user_specified_cropped_directories_individually(
                [self.VALID_SAMPLE_DIR1, self.VALID_SAMPLE_DIR2]
            )
        )

    def test_user_mixes_individual_and_single_valid(self):
        """
        The user mixes indiviudally specified directories with "valid" samples directories.
        We should return true
        """
        t_dirs = [
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir1"),
        ]

        # With one valid sample directory at the list end
        t_1 = t_dirs
        t_1.append(self.VALID_SAMPLE_DIR1)
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_1))

        # With one valid sample directory at the list start
        t_2 = t_dirs
        t_2.insert(0, self.VALID_SAMPLE_DIR1)
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_2))

    def test_user_specifies_one_directory_from_a_cropped_acq(self):
        """
        Should return True because this is a cropped sample.
        """
        out = tts.user_specified_cropped_directories_individually(
            join(self.CROPPED_ACQ_DIR1, "dir1")
        )
        self.assertTrue(out)

    def test_identify_missed_raw_data_archive(self):
        """
        Check whether, we correctly identify a list of source directories as being problematic
        for not having raw data being sent.
        """
        f_1 = [
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir2"),
        ]
        self.assertTrue(tts.issue_warning_if_compressed_data_will_not_be_sent(f_1))

    def test_identify_acceptable_individually_specified_dirs(self):
        """
        Check whether directories specified individually are are nontheless OK
        """

        # Should pass because user supplies compressed archive
        t_1 = [
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir2"),
            join(self.CROPPED_ACQ_DIR1, "compressed_rawData.tar.bz"),
        ]

        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_1))

        # Should pass because specified dirs are in a directory with no compressed data
        crop_no_comp_dat = join(
            self.DATA_DIR, "contains_data_subfolders_no_compress_data"
        )
        t_2 = [join(crop_no_comp_dat, "dir1"), join(crop_no_comp_dat, "dir2")]
        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_2))

    def test_compressed_data_warning_with_normal_call_structure(self):
        """
        Test whether a normal call structure (e.g. a cropped root dir) will trigger no error
        """

        self.assertFalse(
            tts.issue_warning_if_compressed_data_will_not_be_sent(
                self.VALID_SAMPLE_DIR1
            )
        )
        self.assertFalse(
            tts.issue_warning_if_compressed_data_will_not_be_sent(
                self.CROPPED_ACQ_DIR1
            )
        )

        # Two directories containing cropped acquisitions should also pass
        t_1 = [self.CROPPED_ACQ_DIR1, self.CROPPED_ACQ_DIR2]
        self.assertFalse(tts.issue_warning_if_compressed_data_will_not_be_sent(t_1))

    def test_identify_peculiar_individually_specified_cases(self):
        """
        The user might mix and match individually specified directories with "normal" directories.
        Check these cases: when in doubt we just want to flag it.
        """

        # f_1 is two individually specified directories aand then after a valid sample dir
        f_1 = [
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir2"),
            self.VALID_SAMPLE_DIR1,
        ]

        # f_2 is a valid sample dir and *then* two individually specified directories
        f_2 = [
            self.VALID_SAMPLE_DIR1,
            join(self.CROPPED_ACQ_DIR1, "dir1"),
            join(self.CROPPED_ACQ_DIR1, "dir2"),
        ]
        self.assertTrue(tts.issue_warning_if_compressed_data_will_not_be_sent(f_1))
        self.assertTrue(tts.issue_warning_if_compressed_data_will_not_be_sent(f_2))
