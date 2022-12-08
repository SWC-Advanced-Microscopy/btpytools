"""
General purpose tools for handling BakingTray data directories
"""

import sys
import os
import re
from glob import glob
from pathlib import Path
import shutil
from datetime import datetime

# Define variables that will be common across functions
STITCHED_IMAGE_DIR = "stitchedImages_*"
RAW_DATA_DIR = "rawData"
DOWNSAMPLED_DIR = "downsampled_stacks"
DOWNSAMPLED_STACK_SUB_DIR = "*_micron"  # Sub-directories in DOWNSAMPLED_DIR
DOWNSAMPLED_STACK_LOG_FILE = "ds_*.txt"  # Wildcard for downsampled stacks
UNCROPPED_WILDCARD = "./Uncropped*_DELETE_ME_DELETE_ME"
RECIPE_WILDCARD = "recipe*.yml"

# Related to registration directories.
ROOT_REG_DIR = "registration"
REG_DIR_REGEX = r"reg_\d{2}__\d{4}_\d{2}_\d{2}_\w"


def has_raw_data(t_path=""):
    """Check if current directory (or that defined by t_path contains a
    rawData directory. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, RAW_DATA_DIR)
    return os.path.isdir(t_path)


def has_compressed_raw_data(t_path=""):
    """Check if current directory (or that defined by t_path has
    compressed raw data. Returns True if present, False if absent
    """
    t_path = os.path.join(t_path, "*rawData*.tar.[gb]z")
    return file_glob_exist(t_path)


def has_recipe_file(t_path=""):
    """Check if current directory (or that defined by t_path contains
    a recipe file. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, RECIPE_WILDCARD)
    return file_glob_exist(t_path)


def has_scan_settings(t_path=""):
    """Check if current directory (or that defined by t_path contains
    a scanSettings.mat file. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, "scanSettings.mat")
    return os.path.isfile(t_path)


def has_stitched_images_directory(t_path=""):
    """Check if current directory (or that defined by t_path contains a
    stitched image directory Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, STITCHED_IMAGE_DIR)
    return file_glob_exist(t_path)


def has_stitched_stacks(t_path=""):
    """Check if current directory (or that defined by t_path contains
    stitched tiff stacks. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, "./*_chan_0[1-9].tiff")
    return file_glob_exist(t_path)


def has_downsampled_stacks(t_path="", verbose=False):
    """Check if current directory (or that defined by t_path contains a
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
    """Check if current directory (or t_path) contains a stitched image
    directory. Returns True if present, False if absent.
    """
    t_path = os.path.join(t_path, UNCROPPED_WILDCARD)
    return file_glob_exist(t_path)


def is_data_folder(dirToTest="", verbose=False):
    """is directory "dirToTest" a BakingTray data directory?
    i.e. it satisfies the following criteria:
     - contains a recipe YML
     - contains a scanSettings.mat file
     - contains one of: stitchedImages directory, stitched stacks,
                     rawData directory, compressed rawData
    """
    if not os.path.exists(dirToTest):
        print("Directory %s does not exist!" % dirToTest)
        return False

    if verbose:
        print('Testing if directory "%s" is a valid sample directory.' % dirToTest)
        print("Directory contents:")
        print(os.listdir(dirToTest))

    if (has_recipe_file(dirToTest) and has_scan_settings(dirToTest)) and (
        has_stitched_stacks(dirToTest)
        or has_stitched_images_directory(dirToTest)
        or has_raw_data(dirToTest)
        or has_compressed_raw_data(dirToTest)
    ):
        return True

    else:
        if verbose:
            print("Test directory is not a data folder:")
            print("Has recipe: %s" % has_recipe_file(dirToTest))
            print("Has scan settings: %s" % has_scan_settings(dirToTest))
            print("Has stitched stacks: %s" % has_stitched_stacks(dirToTest))
            print(
                "Has stitched images directory: %s"
                % has_stitched_images_directory(dirToTest)
            )
            print("Has raw data: %s" % has_raw_data(dirToTest))
            print("Has compressed raw data: %s" % has_compressed_raw_data(dirToTest))

        return False


def contains_data_folders(dirToTest, verbose=False):
    """returns true if dirToTest contains sub-directories that are
    BakingTray data folders.
    """
    subDirs = next(os.walk(dirToTest))[1]

    if len(subDirs) == 0:
        return False

    for tDir in subDirs:
        path_to_test = os.path.join(dirToTest, tDir)
        if not os.path.exists(path_to_test):
            print("Directory %s does not exist!" % path_to_test)
            return False

        if verbose:
            print('Testing if "%s" is a data folder: ' % path_to_test, end="")

        if is_data_folder(path_to_test):
            if verbose:
                print("YES")
            return True

        else:
            if verbose:
                print("NO")
                dir_contents = os.listdir(path_to_test)
                if len(dir_contents) == 0:
                    print("Directory is empty")
                else:
                    print("Directory contents:")
                    print(dir_contents)

    # If we're here then there are no data-containing subdirs
    return False


def available_downsampled_volumes(in_path="", verbose=False):
    """Check if current directory (or that defined by t_path contains a ownsampled stacks
    directory and returns a list of dictionaries listing the available downsampled data.
    If none are present returns False.
    """
    if not has_downsampled_stacks(in_path, verbose):
        return False

    # This defines the downsampled stack directory and what the downsampled
    # stacks are called. The following line can have two layers of wildcards.
    # e.g. downsampled_stacks/*_micron/ds_*.txt
    in_path = os.path.join(
        in_path,
        DOWNSAMPLED_DIR,
        DOWNSAMPLED_STACK_SUB_DIR,
        DOWNSAMPLED_STACK_LOG_FILE,
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
    """Parse StitchIt downsampled data file and return as a dictionary
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
    s = re.search(r".*(\d+)_micron", pathToFile)
    out["voxelsize"] = int(s.group(1))

    # Get the channel index from the file name
    s = re.search(r".*_ch(0\d+)", pathToFile)
    out["channelindex"] = int(s.group(1))

    # Get the channel friendly name from the file name
    s = re.search(r".*_ch\d+_chan_\d_(.*)\.t", pathToFile)
    if s is not None:
        out["channelname"] = s.group(1)
    else:
        out["channelname"] = str(out["channelindex"])

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
            sys.stdout.write(
                "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
            )


def in_tmux_session():
    """Return true if we are running in a tmux session"""
    if os.popen("echo $TERM").read().strip() == "screen":
        return True
    else:
        return False


def in_ssh_session():
    """Return true if we are in an SSH session"""
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


def get_dir_size_in_GB(t_path, fast_raw_data=False):
    """
    Return the size of directory t_path in GB.
    Return False if directory dow not exist

    If fast_raw_data is true, we assume this is a raw data
    directory and measure the size of every 10th sub-dir then
    multiply by 10 to estimate the full size.
    """

    if not file_glob_exist(t_path):
        return False

    if fast_raw_data:
        t_path = Path(t_path).glob("*-*1/*")
    else:
        t_path = Path(t_path).glob("**/*")

    size_in_bytes = sum(f.stat().st_size for f in t_path if f.is_file())

    if fast_raw_data:
        size_in_bytes = (
            size_in_bytes * 10
        )  # Because we measured every 10th directory
        size_in_bytes = size_in_bytes * 1.03  # Because we skipped some directories

    return size_in_bytes / 1024**3


def get_free_disk_space_in_GB(t_path="."):
    """
    Return free disk space in GB. Uses volume associated with current path if no
    path is provided.
    """

    out = shutil.disk_usage(t_path)
    return out.free / 1024**3


def cli_question(text, valid_answers, default_answer=False, error_string=""):
    """
    Ask a multiple choice question at CLI and returb user choice

    Inputs
    text - string to present to user
    valid answers - list of valid answers that can be provided
    default_answer - an integer indicating which element in valid_answers is the default
    error_string - string to present if for some reason the user's response is not valid
    """

    reply = ""

    print("%s" % text)
    second_pass = False

    while True:

        if second_pass:
            if len(error_string) > 0:
                print(error_string)
            else:
                print(text)

        if default_answer is False:
            reply = input("? ")
        else:
            # If the user selects the default answer we just return this
            reply = input("[%s] ? " % (default_answer + 1))
            if len(reply) == 0:
                return valid_answers[default_answer]

        second_pass = True

        # If a valid reply is provided, we break and return it. Otherwise keep looping
        if reply in valid_answers:
            break

    return reply


def find_reg_dirs(verbose=True):
    """
    Looks for existing registration sub-directories

    Purpose
    Return absolute paths to existing registration sub-directories made by
    the function aratools.make_reg_dir

    Outputs
    existing_reg_dirs - list of absolute paths to all existing registration directories
    """

    reg_dir = os.path.abspath(ROOT_REG_DIR)
    existing_reg_dirs = list()

    if verbose:
        print("Looking for registration directories in path %s" % reg_dir)

    if not os.path.exists(reg_dir):
        if verbose:
            print("find_reg_dirs can not find path %s" % reg_dir)
        return existing_reg_dirs

    existing_sub_dirs = [x[0] for x in os.walk(reg_dir)]

    if len(existing_sub_dirs) == 0:
        if verbose:
            print("find_reg_dirs finds no sub-directories in path %s" % reg_dir)
        return existing_reg_dirs

    for t_dir in existing_sub_dirs:
        if re.match(REG_DIR_REGEX, os.path.basename(t_dir)):
            existing_reg_dirs.append(t_dir)

    return existing_reg_dirs


def make_reg_dir(simulate=False):
    """
    ARA helper function. Makes directories for registration within the current directory

    pathToRegDir = make_reg_dir

    Purpose
    Make a directory into which we will register data. Return the path as a string.
    Makes directories in the form:

    registration/reg_01__2020_03_19_a
    registration/reg_02__2020_03_19_b
    registration/reg_03__2020_03_20_a
    etc..

    Within each the following will be created by ARAregister:
    registration/reg_01__2020_03_19_a/ARA_to_sample
    registration/reg_01__2020_03_19_a/sample_to_ARA

    Outputs
    pathToRegDir - absolute path to the just-made registration directory

    """

    if simulate:
        print("Running tools.make_reg_dir()")

    reg_dir = os.path.abspath(ROOT_REG_DIR)

    if not os.path.exists(reg_dir):
        if simulate:
            print("Making directory %s" % reg_dir)
        else:
            os.mkdir(reg_dir)

    sub_dir_names = find_reg_dirs()

    # Make the registration sub-directory
    today_date = datetime.now().strftime("%Y_%m_%d")
    if not sub_dir_names:
        # If there are no registration sub-directories then we make one.
        reg_dir_to_make = "reg_01__%s_a" % today_date
    else:
        # Otherwise registrations already exist. We make a new directory that
        # increments the previous one:
        last_dir_name = os.path.basename(sub_dir_names[-1])

        reg_index = re.search(r"reg_(\d{2})", last_dir_name)

        # The number of directories that contain today's date
        n_dirs = len([d for d in sub_dir_names if today_date in d])

        reg_dir_to_make = "reg_%02d__%s_%s" % (
            int(reg_index.group(1)) + 1,
            today_date,
            increment_char("a", n_dirs),
        )

    full_path_to_make = os.path.join(reg_dir, reg_dir_to_make)

    if simulate:
        print("Making directory %s" % full_path_to_make)
    else:
        os.mkdir(full_path_to_make)

    return full_path_to_make


def make_log_dir():
    print("hello")


def increment_char(t_char, increment_by=1):
    """
    Increment character to next highest for making file names
    """

    o_char = ord(t_char)

    # Increment
    o_char += increment_by

    # 122 is "z" so next go to "A" if we are here
    if o_char > 122:
        o_char -= 58

    return chr(o_char)
