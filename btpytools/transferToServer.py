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
import sys
from btpytools import tools, recipe
from textwrap import dedent  # To remove common leading white-space
import argparse


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
    'acq_123/acq1', etc. If they have done the latter, this function returns true. 

    Inputs: 
    source_dirs - a list of source directories
    
    Outputs
    False means the user did not specify cropped directories individually. 
    True means that at least two directories in the input list are from the same
    cropped acquisition. 

    Notes:
    - Function returns true even if some samples nested within the parent directory
      were not supplied. 
    """

    # If the list is only one directory long then we are unlikely to have anything
    # cropped so we can just bail out.
    if len(source_dirs) == 1:
        return False

    # Remove everything from the list that is not a directory
    source_dirs = [x for x in source_dirs if os.path.isdir(x)]


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
