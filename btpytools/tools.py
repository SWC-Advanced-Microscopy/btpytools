"""
General purpose tools for handling BakingTray data directories
"""

import sys
import os
import re
from glob import glob
from pathlib import Path
import shutil

# Define variables that will be common across functions
STITCHED_IMAGE_DIR = "stitchedImages_*"
RAW_DATA_DIR = "rawData"
DOWNSAMPLED_DIR = "downsampled_stacks"
DOWNSAMPLED_STACK_SUB_DIR = "*_micron"  # Sub-directories in DOWNSAMPLED_DIR
DOWNSAMPLED_STACK_LOG_FILE = "ds_*.txt"  # Wildcard for downsampled stacks
UNCROPPED_WILDCARD = "./Uncropped*_DELETE_ME_DELETE_ME"
RECIPE_WILDCARD = "recipe*.yml"


def has_raw_data(t_path=""):
    """ Check if current directory (or that defined by t_path) contains a
        rawData directory. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, RAW_DATA_DIR)
    return os.path.isdir(t_path)


def has_compressed_raw_data(t_path=""):
    """ Check if current directory (or that defined by t_path) has
        compressed raw data. Returns True if present, False if absent
    """
    t_path = os.path.join(t_path, "*rawData*.tar.[gb]z")
    return file_glob_exist(t_path)


def has_recipe_file(t_path=""):
    """ Check if current directory (or that defined by t_path) contains
        a recipe file. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, RECIPE_WILDCARD)
    return file_glob_exist(t_path)


def has_scan_settings(t_path=""):
    """ Check if current directory (or that defined by t_path) contains
        a scanSettings.mat file. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, "scanSettings.mat")
    return os.path.isfile(t_path)


def has_stitched_images_directory(t_path=""):
    """ Check if current directory (or that defined by t_path) contains a
        stitched image directory Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, STITCHED_IMAGE_DIR)
    return file_glob_exist(t_path)


def has_stitched_stacks(t_path=""):
    """ Check if current directory (or that defined by t_path) contains
        stitched tiff stacks. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, "./*_chan_0[1-9].tiff")
    return file_glob_exist(t_path)


def has_downsampled_stacks(t_path="", verbose=False):
    """ Check if current directory (or that defined by t_path) contains a
        downsampled_stacks directory. Returns True if present, False if absent.
    """

    # Is there a downsampled stack dir?
    t_path = os.path.join(t_path, DOWNSAMPLED_DIR)

    if not file_glob_exist(t_path):
        if verbose:
            print("Can not find path %s" % t_path)

        return False

    # Does the downsampled stack directory contain downsampled stack directories?
    if not file_glob_exist(os.path.join(t_path, DOWNSAMPLED_STACK_SUB_DIR)):
        if verbose:
            print(
                "Downsampled stack directory does not contain downsampled stack sub-dirs"
            )
        return False

    return file_glob_exist(t_path)


def has_uncropped_stitched_images(t_path=""):
    """ Check if current directory (or t_path) contains a stitched image
        directory. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, UNCROPPED_WILDCARD)
    return file_glob_exist(t_path)


def is_data_folder(dirToTest):
    """ is directory "dirToTest" a BakingTray data directory?
       i.e. it satisfies the following criteria:
        - contains a recipe YML
        - contains a scanSettings.mat file
        - contains one of: stitchedImages directory, stitched stacks,
                        rawData directory, compressed rawData
    """
    if (has_recipe_file(dirToTest) and has_scan_settings(dirToTest)) and (
        has_stitched_stacks(dirToTest)
        or has_stitched_images_directory(dirToTest)
        or has_raw_data(dirToTest)
        or has_compressed_raw_data(dirToTest)
    ):
        return True
    else:
        return False


def contains_data_folders(dirToTest):
    """ returns true if dirToTest contains sub-directories that are
        BakingTray data folders.
    """
    subDirs = next(os.walk(dirToTest))[1]
    if len(subDirs) == 0:
        return False
    for tDir in subDirs:
        if is_data_folder(os.path.join(dirToTest, tDir)):
            return True

    # If we're here then there are no data-containing subdirs
    return False


def available_downsampled_volumes(in_path="", verbose=False):
    """ Check if current directory (or that defined by t_path) contains a ownsampled stacks
        directory and returns a list of dictionaries listing the available downsampled data.
        If none are present returns False.
    """
    if not has_downsampled_stacks(in_path, verbose):
        return False

    # This defines the downsampled stack directory and what the downsampled
    # stacks are called. The following line can have two layers of wildcards.
    # e.g. downsampled_stacks/*_micron/ds_*.txt
    in_path = os.path.join(
        in_path, DOWNSAMPLED_DIR, DOWNSAMPLED_STACK_SUB_DIR, DOWNSAMPLED_STACK_LOG_FILE
    )
    paths_to_downsampled_stacks = glob(in_path)

    if len(paths_to_downsampled_stacks) < 1:
        if verbose("No downsampled stacks found"):
            return False

    out = []
    for t_path in paths_to_downsampled_stacks:
        t_log = read_downsample_log_file(t_path)
        out.append(t_log)

    return out


def read_downsample_log_file(pathToFile=""):
    """ Parse StitchIt downsampled data file and return as a dictionary
        pathToFile is the path to a dowsampled log file returns False if
        no data are found in the defined path or multiple paths were supplied.
    """

    if len(pathToFile) < 1:
        return False
    elif isinstance(pathToFile, list) and len(pathToFile) == 1:
        pathToFile = pathToFile[0]
    elif isinstance(pathToFile, list) and len(pathToFile) > 1:
        return False

    with open(pathToFile) as ff:
        lines = ff.readlines()

    # Make a dictionary from the file contents
    out = dict()

    # Sample name
    s = re.search("Downsampling (.*)", get_line_with_substr(lines, "Downsampling"))
    out["samplename"] = s.group(1)

    # Downsampled file name
    s = re.search(
        "downsample file name: (.*)",
        get_line_with_substr(lines, "downsample file name"),
    )
    out["path2stack"] = s.group(1)

    # Acquisition date
    s = re.search("Acquired on: (.*)", get_line_with_substr(lines, "Acquired"))
    out["acqdate"] = s.group(1)

    # Get the voxel size from the directory name
    s = re.search(r".*/(\d+)_micron/", pathToFile)
    out["voxelsize"] = int(s.group(1))

    # Get the channel index from the file name
    s = re.search(r".*_ch(\d+)_chan_\d_", pathToFile)
    out["channelindex"] = int(s.group(1))

    # Get the channel friendly name from the file name
    s = re.search(r".*_ch\d+_chan_\d_(.*)\.t", pathToFile)
    out["channelname"] = s.group(1)

    return out


"""
The following are very general purpose and not specific to BakingTray
"""


def file_glob_exist(t_path):
    if len(glob(t_path)) == 0:
        return False
    else:
        return True


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def in_tmux_session():
    """ Return true if we are running in a tmux session
    """
    if os.popen("echo $TERM").read().strip() == "screen":
        return True
    else:
        return False


def in_ssh_session():
    """ Return true if we are in an SSH session
    """
    if len(os.popen("echo $SSH_CONNECTION").read().strip()) > 0:
        return True
    else:
        return False


def get_line_with_substr(allLines, subStr):
    """Return line from list of strings that contains a substring
       False if nothing is found
       Returns a list if multiple lines found
    """

    tLine = [myS for myS in allLines if subStr in myS]

    if len(tLine) < 1:
        return False

    if len(tLine) == 1:
        return tLine[0].rstrip()
    else:
        return tLine


def get_dir_size_in_GB(t_path):
    """
    Return the size of directory t_path in GB.
    Return False if directory dow not exist
    """

    if not file_glob_exist(t_path):
        return False

    t_path = Path(t_path)
    size_in_bytes = sum(f.stat().st_size for f in t_path.glob("**/*") if f.is_file())
    return size_in_bytes / 1024 ** 3


def get_free_disk_space_in_GB(t_path="."):
    """
    Return free disk space in GB. Uses volume associated with current path if no
    path is provided.
    """

    out = shutil.disk_usage(t_path)
    return out.free / 1024 ** 3
