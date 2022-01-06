import unittest
import os
from btpytools import transferToServer as tts
from btpytools import tools

'''
Run with "pytest tests/tests/basic.py" from project root
'''

data_dir = os.path.join("tests", "data")
valid_sample_dir =  os.path.join(data_dir,'valid_sample_directory')

class test_tools(unittest.TestCase):
    '''
    Run tests associated with btpytools.tools
    '''
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
        t_path = os.path.join(data_dir,'contains_data_subfolders')
        self.assertTrue(tools.has_uncropped_stitched_images(t_path))


    def test_invalid_directories_are_invalid(self):
        invalid_dir = os.path.join(data_dir,'invalid_data_dirs')

        for t_path in os.listdir(invalid_dir):
            self.assertFalse(tools.is_data_folder(os.path.join(invalid_dir,t_path)))


    def test_contains_data_subfolders(self):
        t_path = os.path.join(data_dir,'contains_data_subfolders')
        self.assertTrue(tools.contains_data_folders)



class test_transfer_to_server(unittest.TestCase):
    '''
    Run tests associated with btpytools.transferToServer
    '''
    def test_check_directories_exist(self):
        OUT = tts.check_directories(os.path.join(data_dir,'dir_a'),
            os.path.join(data_dir,'dir_b'))
        self.assertTrue(True)
