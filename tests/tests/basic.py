import unittest
import os
from os.path import join
from btpytools import transferToServer as tts
from btpytools import tools

"""
Run with "pytest tests/tests/basic.py" from project root
"""

data_dir = join("tests", "data")
valid_sample_dir = join(data_dir, "valid_sample_directory")
cropped_acq_dir = join(data_dir, "contains_data_subfolders")

class test_tools(unittest.TestCase):
    """
    Run tests associated with btpytools.tools
    """

    def test_valid_directory_is_valid(self):
        self.assertTrue(tools.is_data_folder(valid_sample_dir))

    def test_has_raw_data(self):
        self.assertTrue(tools.has_raw_data(valid_sample_dir))

    def test_has_compressed_raw_data(self):
        self.assertTrue(tools.has_compressed_raw_data(valid_sample_dir))

    def test_has_recipe_file(self):
        self.assertTrue(tools.has_recipe_file(valid_sample_dir))

    def test_has_recipe_file(self):
        self.assertTrue(tools.has_scan_settings(valid_sample_dir))

    def test_has_stitched_images_directory(self):
        self.assertTrue(tools.has_stitched_images_directory(valid_sample_dir))

    def test_uncropped_stitched_images(self):
        self.assertTrue(tools.has_uncropped_stitched_images(cropped_acq_dir))

    def test_invalid_directories_are_invalid(self):
        invalid_dir = join(data_dir, "invalid_data_dirs")

        for t_path in os.listdir(invalid_dir):
            self.assertFalse(tools.is_data_folder(join(invalid_dir, t_path)))

    def test_contains_data_subfolders(self):
        self.assertTrue(tools.contains_data_folders(cropped_acq_dir))


class test_transfer_to_server(unittest.TestCase):
    """
    Run tests associated with btpytools.transferToServer.
    Some functions within this module are hard to understand without the tests
    """

    def test_check_directories_exist(self):
        OUT = tts.check_directories(
            join(data_dir, "dir_a"), join(data_dir, "dir_b")
        )
        self.assertTrue(True)

    def test_dir_list_contains_compressed_archive(self):
        a1 = ['dir1/dir2/stuff_rawData.tar.bz','dir_a','dir_b']
        a2 = ['dir1/dir2/stuff_rawData.tar.gz','dir_a','dir_b']
        a3 = ['dir1/dir2/stuff_rawData.tar.gz','dir_a','dir_b','dir1/dir2/stuff_rawData.tar.bz']
        self.assertTrue(tts.dir_list_contains_compressed_archive(a1))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a2))
        self.assertTrue(tts.dir_list_contains_compressed_archive(a3))

    def test_dir_list_not_contains_compressed_archive(self):
        b1 = ['dir1/dir2','dir_a','dir_b']
        b2 = ['dir1/dir2/stuff_rawData.tar','dir_a','dir_b']
        b3 = ['dir1/dir2/stuff_rawData','dir_a','dir_b','dir1/dir2/rawData']
        self.assertFalse(tts.dir_list_contains_compressed_archive(b1))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b2))
        self.assertFalse(tts.dir_list_contains_compressed_archive(b3))

    def test_user_specified_individual_dirs(self):
        '''
        User specifies two cropped samples within a single acquisition
        '''
        t_dirs = [join(cropped_acq_dir,'dir1'),join(cropped_acq_dir,'dir1')]
        self.assertTrue(tts.user_specified_cropped_directories_individually(t_dirs))

    def test_user_specifies_one_valid_directory(self):
        '''
        Should return False because this is not a cropped sample
        '''
        self.assertFalse(tts.user_specified_cropped_directories_individually(valid_sample_dir))

    def test_user_specifies_one_directory_from_a_cropped_acq(self):
        '''
        Should return True because this is a cropped sample
        '''
        self.assertTrue(tts.user_specified_cropped_directories_individually(join(cropped_acq_dir,'dir1')))