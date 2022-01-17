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
from btpytools import tools
from textwrap import dedent  # To remove common leading white-space
import argparse
import re


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
                               $ transferToServer ./XY_123 /mnt/datastor/user/path/

                            2. Transfer a directory containing two samples (after cropping) plus any compressed raw data.
                               You will be prompted whether you want the source data to be copied in the enclosing directory.
                               $ transferToServer ./USER_sampleA_sampleB/ /mnt/datastor/user/path/

                               Note, this is the same as doing:
                               $ transferToServer ./USER_sampleA_sampleB/sample1 ./USER_sampleA_sampleB/sample2 ./USER_sampleA_sampleB/rawData.tar.bz /mnt/datastor/user/path/

                            3. Simulate the transfer of one sample
                               $ transferToServer ./XY_123 /mnt/datastor/user/path/ -s

                            4. Run with different rsync flags
                               $ transferToServer ./XY_123 /mnt/datastor/user/path/ -r rv

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
        help='If supplied, this rsync flag is used. Default is "av". Other reasonable options include "rv".',
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


def user_specified_cropped_directories_individually(source_dirs):
    """
    Checks whether the user has manually supplied multiple split sample directories
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

    # If the list is only one directory long (or is a string) then we are unlikely to have anything
    # cropped so we can just bail out.
    if (
        isinstance(source_dirs, str)
        or isinstance(source_dirs, list)
        and len(source_dirs) == 1
    ):
        return False

    # TODO -- the above is only true if the directory it sits in is not a cropped data directory
    # It is possible user specified just one directory from a cropped acquisition.

    # Remove everything from the list that is not a directory
    source_dirs = [x for x in source_dirs if os.path.isdir(x)]

    # First we handle the potential scenario where the user's current folder is a
    # data acquisition directory.
    cwd_is_data_dir = tools.is_data_folder(os.getcwd())

    if cwd_is_data_dir:
        # If the current directory is a BakingTray data folder and there are multiple source
        # directories then the user has, indeed, specified directories individually.
        return True

    else:
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
            return True

        # At this point we know that source_dirs was a directory list that probably something of
        # this sort: './acq_xy/sample1' , './acq_ab/sample1'. This is an unusual scenario and,
        # like in the if statement above, means the user is specifying directories from a cropped
        # acquisition individually. We therefore return True.
        return True


def dir_list_contains_compressed_archive(source_dirs):
    """
    Does the directory list in source_dirs contain at least one compressed raw data archive?
    The lack of a compressed archive in this list does not meant the compressed raw data are
    not going to be sent. It just reflects whether or not the user has explicitly asked to send the data.

    This function is used in conjunction with others to determine whether there is a
    chance that the user is accidentally failing to back up compressed raw data.

    Inputs:
    source_dirs - a list of source directories

    Outputs
    True means the directory list in source_dirs contains a raw data archive. False otherwise.
    """

    compressed_archives = [
        x
        for x in source_dirs
        if isinstance(re.match(r".*rawData.*\.tar\.[bg]z", x), re.Match)
    ]

    if len(compressed_archives) > 0:
        return True
    else:
        return False


def main():
    """
    main()
    """

    # Process arguments and set up
    args = cli_parser().parse_args()

    if len(args.paths) < 2:
        print(
            "\n\n ERROR: transferToServer requires at least one local path to copy and a destination\n"
        )
        print(' See "transferToServer -h"\n')
        exit()

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
        exit()

    # Remove trailing slash from data directories that don't contain data sub-directories
    for ii, tDir in enumerate(source_dirs):
        if tools.is_data_folder(tDir) and not tools.contains_data_folders(tDir):
            # If here, tDIR is a sample folder without sub-folders. If there is a
            # trailing slash then we should delete it. Always.
            if tDir[-1] == os.path.sep:
                source_dirs[ii] = tDir[0:-1]

        elif tools.contains_data_folders(tDir):
            # If here, tDIR contains sub-folders which are sample folders. Thus is likely
            # contains cropped data. We again delete the trailing slash but we give the
            # user the option to add it back, copying the *contents* to the destination
            # rather than in the enclosing folder.
            if tDir[-1] == os.path.sep:
                source_dirs[ii] = tDir[0:-1]

            print('\nDirectory "%s" contains multiple samples.' % tDir)
            print(
                "Do you want to keep samples in their enclosing directory (%s) when on the server?"
                % tDir
            )
            if not tools.query_yes_no(""):
                # Add trailing slash, if user does not want to keep enclosing folder.
                source_dirs[ii] = source_dirs[ii] + os.path.sep

    print("")

    # Check whether any of the directories we plan to copy already exist at the destination
    safeToCopy = True
    for ii, tDir in enumerate(source_dirs):

        if tDir[-1] != os.path.sep:
            # Look for this directory at the destination
            destinationPath = os.path.join(destination_dir, tDir)
            if os.path.exists(destinationPath):
                safeToCopy = False
                print(
                    '===>>> WARNING!! "%s" already exists in "%s"!! Proceeding will over-write its contents <===='
                    % (tDir, destination_dir)
                )
        else:
            # Look for the *contents* of this directory at the destination
            dirContents = os.listdir(tDir)
            for jj, subDir in enumerate(dirContents):
                if subDir == "rawData" or "_DELETE_ME" in subDir:
                    continue
                destinationPath = os.path.join(destination_dir, subDir)
                if os.path.exists(destinationPath):
                    safeToCopy = False
                    print(
                        '===>>> WARNING!! "%s" already exists in "%s"!! Proceeding will over-write its contents <===='
                        % (subDir, destination_dir)
                    )

    if safeToCopy == False:
        print("\n IS IT OK TO PROCEED DESPITE THE ABOVE WARNINGS?")
        if not tools.query_yes_no(""):
            exit()

    # Ask for confirmation before starting
    print("\nPerform the following transfer?")
    for ii, tDir in enumerate(source_dirs):
        if tDir[-1] != os.path.sep:
            print('Copy directory "%s" to location "%s"' % (tDir, destination_dir))
        else:
            dirContents = os.listdir(tDir)
            for jj, subContents in enumerate(dirContents):
                if subContents == "rawData" or subContents.endswith("_DELETE_ME"):
                    pass
                else:
                    print('Copy "%s" to "%s"' % (subContents, destination_dir))

    # Build the rsync command string
    cmd = "rsync %s --progress --exclude rawData --exclude *_DELETE_ME_* %s %s " % (
        main_rsync_switch,
        " ".join(source_dirs),
        destination_dir,
    )

    print("Using command %s" % cmd)
    if not tools.query_yes_no(""):
        exit()

    # Start the transfer
    os.system(cmd)


if __name__ == "__main__":
    main()
