from os.path import join


class btpytools_test:
    """Provides common data that will be needed by multiple test classes.
    Test classes can inherit this to access the data as attributes.
    """

    DATA_DIR = join("tests", "data")
    VALID_SAMPLE_DIR1 = join(DATA_DIR, "valid_sample_directory_01")
    VALID_SAMPLE_DIR2 = join(DATA_DIR, "valid_sample_directory_02")
    CROPPED_ACQ_DIR1 = join(DATA_DIR, "contains_data_subfolders_01")
    CROPPED_ACQ_DIR2 = join(DATA_DIR, "contains_data_subfolders_02")
