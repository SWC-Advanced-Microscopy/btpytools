#!/usr/bin/env python3

""" Transfer BrainSaw data to a server mounted on the local machine

This function is a wrapper round rsync and is used for copying BakingTray
data to a server over a network connection.

Input arguments
- one or more paths to local directories which are to be copied
- the last path is the destination.

transferToServer ./localSampleA ./localSampleB /path/to/server

For more see transferToServer -h


Notes
If you have signed in via SSH and aren't in a tmux session, the function
asks for confirmation before continuing. If your ssh session breaks off
for some reason, then compression will fail. tmux is therefore recommended
in this situation.

"""


import os
import argparse
import re
import sys
import subprocess
from textwrap import dedent  # To remove common leading white-space
from btpytools import tools
from termcolor import colored


def cli_parser():
    """
    Build and return an argument parser
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="transferToServer",
        description=dedent(
            """\
        Transfer BrainSaw data to a server mounted on the local machine

        This function is a wrapper round rsync and is used for copying BakingTray
        data to a server. It automatically does not copy uncompressed raw data or
        the un-cropped stacks directory.

        Input arguments
        - one or more paths to local directories which are to be copied
        - the last path is the destination.


        Usage examples:

        1. Transfer one sample plus any compressed raw data:
           $ transferToServer ./XY_123 /mnt/datastor/

        2. Transfer a directory containing two samples (after cropping) plus any
           compressed raw data. You will be prompted whether you want the source data
           to be copied in the enclosing directory.
           $ transferToServer ./dataA_B/ /mnt/server/

           Note, this is the same as doing:
           $ transferToServer ./dataA_B/sampA ./dataA_B/sampB ./dataA_B/rawData.tar.bz /mnt/server/

        3. Simulate the transfer of one sample
           $ transferToServer ./XY_123 /mnt/datastor/ -s

        4. Run with different rsync flags
           $ transferToServer ./XY_123 /mnt/datastor/ -r rv

        """
        ),
        epilog=dedent(
            """\
                Notes
                If you have signed in via SSH and aren't in a tmux session, the function
                asks for confirmation before continuing. If your ssh session breaks off
                for some reason, then compression will fail. tmux is therefore recommended
                in this situation.
            """
        ),
    )

    parser.add_argument(
        dest="paths",
        type=str,
        nargs="+",
        help="One or more local paths followed by destination path",
    )

    parser.add_argument(
        "-s",
        "--simulate",
        dest="simulate",
        required=False,
        action="store_true",
        help="If supplied an rsync dry run is conducted and nothing is copied.",
    )

    parser.add_argument(
        "-r",
        "--rsync_flags",
        dest="rsync_flags",
        required=False,
        default="av",
        type=str,
        help=(
            "If supplied, this rsync flag is used. "
            'Default is "av". Other reasonable options include "rv".'
        ),
    )

    return parser


def check_directories(source_dirs, destination_dir):
    """
    Returns True if the source and destination directories are all valid.
    False otherwise. This allows main() to bail out if, for instance, any
    of the supplied paths do not exist.
    """
    fail = False
    for tPath in source_dirs:
        if not os.path.exists(tPath):
            print("%s does not exist" % tPath)
            fail = True

    # At least check if the target location is a directory
    if not os.path.isdir(destination_dir):
        print("%s is not a valid destination directory" % destination_dir)
        fail = True

    return fail


def user_specified_cropped_directories_individually(source_dirs, verbose=False):
    """
    Checks whether the user has manually supplied any multiple split sample directories
    from a cropped acquisition. e.g. Say we have a folder called 'acq_123', which
    contains cropped samples 'acq_1', 'acq_2', and 'acq_3'. The user could either provide
    'acq_123' as the source or they could provide a list of all three directories:
    'acq_123/acq1', etc. If they have done the latter, this function returns True.

    This function is used in conjunction with others to determine whether there is a
    chance that the user is accidentally failing to back up compressed raw data.

    Inputs:
    source_dirs - a list of source directories. If just one entry it can be a string.

    Outputs
    False means the user did not specify cropped directories individually.
    True means that at least two directories in the input list are from the same
    cropped acquisition.

    Notes:
    - Function returns true even if some samples nested within the parent directory
      were not supplied.
    """

    # If the list is only one directory long (or is a string) then we still need to check if it
    # is a cropped directory before deciding for sure wether to return True or False.
    if isinstance(source_dirs, list) and len(source_dirs) == 1:
        source_dirs = source_dirs[0]

    if isinstance(source_dirs, str):
        if tools.has_compressed_raw_data(os.path.split(source_dirs)[0]):
            # Parent directory contains a compressed archive. This makes it
            # likely this was a cropped directory and that the user could
            # potentially be failing to include the archive in the list of
            # to transfer (although we will check this elsewhere). If there is no
            # compressed archive this will return False, which is OK.
            return True
        else:
            return False

    # Remove everything from the list that is not a directory
    source_dirs = [x for x in source_dirs if os.path.isdir(x)]

    # Remove any directories that are definitely single samples or uncropped acquisitions
    source_dirs = remove_single_samples_from_list(source_dirs)
    if len(source_dirs) == 0:
        # If list is empty we have no individually specified directories
        return False

    # Now we handle the potential scenario where the user's current folder is a
    # data acquisition directory.
    if tools.is_data_folder(os.getcwd()):
        # If the current directory is a BakingTray data folder and there are multiple source
        # directories (if here theen there are) then the user has, indeed, specified directories
        # individually.
        if verbose:
            print("Individually specified because current dir is a data dir")
        return True

    # Generate a new version of source_dirs with the last element of each path removed
    trimmed_list = [os.path.dirname(x) for x in source_dirs]

    # Since the current directory is not a sample directory, list entries that are empty
    # are in the current directory and therefore are either single samples or acquisitions
    # with multiple samples. We therefore can remove these.
    trimmed_list = [x for x in trimmed_list if len(x) > 0]

    # If the list is now empty, then it contains no individually specified directories
    # from within a cropped acquisition. This is because a list like this will all end
    # up being empty after the above: ['./sample_01', 'sample_02']
    if len(trimmed_list) == 0:
        return False

    # If the list contains two or more non-unique paths, then original source list contained
    # individually specified directories from within a cropped acquisition.
    if len(set(trimmed_list)) != len(trimmed_list):
        # There are duplicates so user must have asked for this
        if verbose:
            print("Duplicates found: must be individually specified")
        return True

    # At this point we know that source_dirs was a directory list that probably something of
    # this sort: './acq_xy/sample1' , './acq_ab/sample1'. This is an unusual scenario and,
    # like in the if statement above, means the user is specifying directories from a cropped
    # acquisition individually. We therefore return True.
    return True


def dir_list_contains_compressed_archive(source_dirs, dir_root="", verbose=False):
    """
    Does the directory list in source_dirs contain at least one compressed raw data archive? The
    lack of a compressed archive in this list does not mean the compressed raw data are not going
    to be sent. It just reflects whether or not the user has explicitly asked to send the data.

    This function is used in conjunction with others to determine whether there is a chance that
    the user is accidentally failing to back up compressed raw data.

    Function looks for a tar.bz or tar.gz archive

    Inputs:
    source_dirs - a list of source directories
    dir_root -  Optional. Empty by default. If present, dir_root restricts the search to only dirs
                that match. See below for examples.

    Outputs
    True means the directory list in source_dirs contains a raw data archive. False otherwise.

    Examples
    source_dirs = ['./sample_dir/sample1', './sample_dir/sample2']
    dir_list_contains_compressed_archive(source_dirs)  # Returns False


    source_dirs = ['./sample_dir/sample1', './sample_dir/sample2', 'sample_dir/rawData.tar.bz']
    dir_list_contains_compressed_archive(source_dirs)  # Returns True


    source_dirs = ['./sample_dir/sample1', './sample_dir/sample2', 'OTHER_DIR/rawData.tar.bz']
    dir_list_contains_compressed_archive(source_dirs)  # Returns True


    source_dirs = ['./sample_dir/sample1', './sample_dir/sample2', 'OTHER_DIR/rawData.tar.bz']
    dir_list_contains_compressed_archive(source_dirs, './sample_dir'')  # Returns False
    """

    # Filter list if needed. This will remove everything that does not match dir_root
    if len(source_dirs) == 0:
        return False

    if verbose:
        print("Searching list for compressed data archive:")
        print(source_dirs)

    if len(dir_root) > 0:
        source_dirs = [i for i in source_dirs if i.startswith(dir_root)]

    if len(source_dirs) == 0:
        print(
            "dir_list_contains_compressed_archive -- Source directories have all been removed. Odd"
        )
        return False

    compressed_archives = [
        x
        for x in source_dirs
        if isinstance(re.match(r".*rawData.*\.tar\.[bg]z", x), re.Match)
    ]

    if len(compressed_archives) > 0:
        return True
    else:
        return False


def issue_warning_if_compressed_data_will_not_be_sent(source_dirs, verbose=False):
    """
    If the user is running transferToServer in a way that would cause raw data not be transfered,
    we return True. If the source directory list appears safe we return False.
    """

    if not user_specified_cropped_directories_individually(source_dirs):
        # Then we are definitely fine and we can return false
        if verbose:
            print("Directories not specified individually")

        return False  # False, nothing is wrong

    # If we are here, there are individually specified directories
    if verbose:
        print("Individually specified directories found")

    # If the user specified the directories individually we are still "safe" so long as either
    # a) They included the compressed archive in the transfer list (source_dirs).
    # b) There is no compressed archive (so the user probably does not want to back up raw data)
    # Go through each directory in the list and confirm the above

    return_state = (
        False  # False, nothing is wrong (unless the loop below modifies this)
    )
    for t_dir in source_dirs:
        if not os.path.isdir(t_dir):
            # Skip if this is not a directory (e.g. it's a raw data archive)
            if verbose:
                print("%s is not a directory: skipping it" % t_dir)
            continue

        print(t_dir, end="")

        parent_dir = os.path.split(t_dir)[0]  # convenience

        if tools.has_compressed_raw_data(t_dir):
            # If true the directory itself contains compressed data.
            print(colored(" has compressed raw data", "green"))
        elif dir_list_contains_compressed_archive(source_dirs, parent_dir):
            # If true, the directory is a split sample and the user has also specified that
            # they want the raw data to be sent.
            print(
                colored(
                    " is a split sample and compressed raw data are being sent",
                    "green",
                )
            )
        elif not dir_list_contains_compressed_archive(
            source_dirs, parent_dir
        ) and tools.has_compressed_raw_data(parent_dir):
            # This sample contains no raw data directory within it, the user did not specify
            # raw data but there *is* raw data in its parent directory. This means the user
            # intended to send the data but is not doing so.
            print(
                colored(
                    " is a split sample with raw data that are not being sent!",
                    "red",
                )
            )
            return_state = True  # We have a problem

    return return_state


def remove_single_samples_from_list(source_dirs, verbose=False):
    """
    Remove from list source_list all folders that are definitely not an individually specified
    directory. Return this list.
    """

    if not isinstance(source_dirs, list):
        return False

    # Remove everything from the list that is not a directory
    source_dirs = [x for x in source_dirs if os.path.isdir(x)]

    if verbose:
        print("\nInitial dir list:\n")
        print(source_dirs)

    # If it has a raw data archive or does not have a cropped directory with the raw data
    # then it is likely a non separately specified directory. So we can remove it from the list.
    # keep removing. If list empty user had none specified indiviudally.
    for t_dir in source_dirs:
        if (
            tools.has_compressed_raw_data(t_dir)
            or tools.has_raw_data(t_dir)
            or tools.has_uncropped_stitched_images(t_dir)
        ):
            if verbose:
                print("Removed %s" % t_dir)
            source_dirs = [x for x in source_dirs if x != t_dir]  # remove t_dir

        if verbose:
            print("Tested %s. length=%s" % (t_dir, len(source_dirs)))

    if len(source_dirs) == 0:
        return list()

    return source_dirs


def main():
    """
    main()
    """

    # Process arguments and set up
    args = cli_parser().parse_args()

    if len(args.paths) < 2:
        print(
            "\n\n ERROR: "
            "transferToServer requires at least one local path to copy and a destination\n"
        )
        print(' See "transferToServer -h"\n')
        sys.exit()

    main_rsync_switch = args.rsync_flags  # This is the flag used by rsync
    if not main_rsync_switch.startswith("-"):
        main_rsync_switch = "-%s" % main_rsync_switch

    # Append "n" for dry-run rsync mode if the user asked for this with the -s flag at CLI
    if args.simulate:
        main_rsync_switch += "n"

    source_dirs = args.paths[0:-1]  # One or more files or folders to copy
    destination_dir = args.paths[-1]  # Where we will copy to

    # Bail out if any of the supplied paths do not exist
    if check_directories(source_dirs, destination_dir):
        sys.exit()

    # Remove trailing slash from data directories that don't contain data sub-directories
    for _ii, t_dir in enumerate(source_dirs):
        if tools.is_data_folder(t_dir) and not tools.contains_data_folders(t_dir):
            # If here, tDIR is a sample folder without sub-folders. If there is a
            # trailing slash then we should delete it. Always.
            if t_dir[-1] == os.path.sep:
                source_dirs[_ii] = t_dir[0:-1]

        elif tools.contains_data_folders(t_dir):
            # If here, tDIR contains sub-folders which are sample folders. Thus is likely
            # contains cropped data. We again delete the trailing slash but we give the
            # user the option to add it back, copying the *contents* to the destination
            # rather than in the enclosing folder.
            if t_dir[-1] == os.path.sep:
                source_dirs[_ii] = t_dir[0:-1]

            print('\nDirectory "%s" contains multiple samples.' % t_dir)
            print(
                "Do you want to keep samples in their enclosing directory (%s) when on the server?"
                % t_dir
            )
            if not tools.query_yes_no(""):
                # Add trailing slash, if user does not want to keep enclosing folder.
                source_dirs[_ii] = source_dirs[_ii] + os.path.sep

    print("")

    # Check whether any of the directories we plan to copy already exist at the destination
    safe_to_copy = True
    for _ii, t_dir in enumerate(source_dirs):

        if t_dir[-1] != os.path.sep:
            # Look for this directory at the destination
            destination_path = os.path.join(destination_dir, t_dir)
            if os.path.exists(destination_path):
                safe_to_copy = False
                print(
                    '===>>> WARNING!! "%s" already exists in "%s"!! '
                    "Proceeding will over-write its contents <===="
                    % (t_dir, destination_dir)
                )
        else:
            # Look for the *contents* of this directory at the destination
            dir_contents = os.listdir(t_dir)
            for _jj, sub_dir in enumerate(dir_contents):
                if sub_dir == "rawData" or "_DELETE_ME" in sub_dir:
                    continue
                destination_path = os.path.join(destination_dir, sub_dir)
                if os.path.exists(destination_path):
                    safe_to_copy = False
                    print(
                        '===>>> WARNING!! "%s" already exists in "%s"!! '
                        "Proceeding will over-write its contents <===="
                        % (sub_dir, destination_dir)
                    )

    if not safe_to_copy:
        print("\n IS IT OK TO PROCEED DESPITE THE ABOVE WARNINGS?")
        if not tools.query_yes_no(""):
            sys.exit()

    # Check whether the user is maybe failing to copy raw data

    if issue_warning_if_compressed_data_will_not_be_sent(source_dirs):
        print(
            "\nYou have specified directories individually and have omitted to "
            "ask for existing compressed raw data to be sent!"
        )
        print("Please see the readme at: https://pypi.org/project/btpytools/")
        if not tools.query_yes_no(
            "Are you sure you want to continue?", default="no"
        ):
            sys.exit()

    # Ask for confirmation before starting
    print("\nPerform the following transfer?")
    for _ii, t_dir in enumerate(source_dirs):
        if t_dir[-1] != os.path.sep:
            print('Copy directory "%s" to location "%s"' % (t_dir, destination_dir))
        else:
            dir_contents = os.listdir(t_dir)
            for _jj, sub_contents in enumerate(dir_contents):
                if sub_contents == "rawData" or sub_contents.endswith("_DELETE_ME"):
                    pass
                else:
                    print('Copy "%s" to "%s"' % (sub_contents, destination_dir))

    # Build the rsync command string
    cmd = "rsync %s --progress --exclude rawData --exclude *_DELETE_ME_* %s %s " % (
        main_rsync_switch,
        " ".join(source_dirs),
        destination_dir,
    )

    print("")

    if not tools.query_yes_no(""):
        sys.exit()

    # Start the transfer and return standard output to the CLI
    os.system(cmd)

    # There are rare cases where the transfer of individual files failed and they became corrupt.
    # Here we see empty files in the destination, whereas in the source they are OK. Re-running the
    # transfer will fix these instances. So we do that here.
    print("\nLooking for corrupted files in destination...\n")
    max_retries = 10
    pass_number = 1

    # Alter the rsync command to add more information
    cmd = cmd.replace("rsync -", "rsync -i")

    while True:
        out = subprocess.check_output(cmd, shell=True)

        # Convert to a string
        out = out.decode()

        # If there are no ">" with -i then nothing was sent
        num_transfered_files = out.count(">")
        if num_transfered_files == 0:
            print("Good! There are no corrupt empty files on the server.")
            break
        else:
            print(
                "Corrected %d corrupt files at destination. Checking again...\n"
                % num_transfered_files
            )

        pass_number += 1
        if pass_number > max_retries:
            print(
                "After %d attempts there still seem to be corrupt files on the server!"
                % max_retries
            )
            break


if __name__ == "__main__":
    main()
