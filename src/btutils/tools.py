"""
General purpose tools for handling BakingTray data directories
"""

import sys
import os
from glob import glob


"""
The following are related to BakingTray data directories
"""

def has_raw_data(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a rawData directory.
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'rawData')
    return os.path.isdir(tPath)


def has_compressed_raw_data(tPath=''):
    """ Check if current directory (or that defined by tPath) has compressed raw data.
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'*rawData*.tar.[gb]z')
    return file_glob_exist(tPath)


def has_recipe_file(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a recipe file.
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'recipe*.yml')
    return file_glob_exist(tPath)


def has_scan_settings(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a scanSettings.mat 
        file. Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'scanSettings.mat')
    return os.path.isfile(tPath)


def has_stitched_images_directory(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a stitched image directory
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'./stitchedImages_*')
    return file_glob_exist(tPath)


def has_stitched_stacks(tPath=''):
    """ Check if current directory (or that defined by tPath) contains stitched tiff stacks
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'./*_chan_0[1-9].tiff')
    return file_glob_exist(tPath)


def has_downsampled_stacks(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a downsampleStacks* directory
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'./downsampledStacks_*')
    return file_glob_exist(tPath)


def has_uncropped_stitched_images(tPath=''):
    """ Check if current directory (or that defined by tPath) contains a stitched image directory
        Returns True if present, False if absent
    """
    tPath = os.path.join(tPath,'./Uncropped*_DELETE_ME_DELETE_ME')
    return file_glob_exist(tPath)


def is_data_folder(dirToTest):
    """ is directory "dirToTest" a BakingTray data directory?
        It does this by asking whether the directory satisfies the following criteria:
        - contains a recipe YML
        - contains a scanSettings.mat file
        - contains one of: stitchedImages directory, stitched stacks, rawData directory, compressed rawData
    """
    if (has_recipe_file(dirToTest) and has_scan_settings(dirToTest)) and \
        (has_stitched_stacks(dirToTest) or has_stitched_images_directory(dirToTest) or \
         has_raw_data(dirToTest) or has_compressed_raw_data(dirToTest)):
        return True
    else:
        return False


def contains_data_folders(dirToTest):
    """ returns true if dirToTest contains sub-directories that are 
        BakingTray data folders
    """
    subDirs = next(os.walk(dirToTest))[1]
    if len(subDirs)==0:
        return False
    for tDir in subDirs:
        if is_data_folder(os.path.join(dirToTest,tDir)):
            return True

    # If we're here then there are no data-containing subdirs
    return False




"""
The following are very general purpose and not specific to BakingTray
"""
def file_glob_exist(tPath):
    if len(glob(tPath)) == 0:
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
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
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
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def in_tmux_session():
    """ Return true if we are running in a tmux session
    """
    if os.popen("echo $TERM").read().strip()=='screen':
        return True
    else:
        return False


def in_ssh_session():
    """ Return true if we are in an SSH session
    """
    if len(os.popen("echo $SSH_CONNECTION").read().strip())>0:
        return True
    else:
        return False
