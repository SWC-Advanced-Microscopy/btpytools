#!/usr/bin/env python3

""" Compress raw data from a BakingTray acquisition to a tar.bz

Usage
cd to sample directory and run this command:
$ cd /mnt/data/somesample
$ compressRawData


Notes
If you have signed in via SSH and aren't in a tmux session, the function
asks for confirmation before continuing. If your ssh session breaks off
for some reason, then compression will fail. tmux is therefore recomended
in this situation.

"""

import os
import time
from btpytools import tools, recipe


def main():
    if tools.has_raw_data() == False:
        print("No rawData folder found in", os.getcwd())
        exit()


    # Generate the compressed file name from the sample name
    compressedRawDataName = recipe.sample_id() + "_rawData.tar.bz"
    print("Found rawData directory for sample " + recipe.sample_id())


    # Begin compression, but warn if we aren't in a tmux session if this is an SSH connection
    if tools.in_ssh_session() and not tools.in_tmux_session():
        if not tools.query_yes_no("\nYou are logged in via SSH but are not in a tmux session, proceed anyway?","no"):
            print("Not proceeding with compression.\n")
            exit()


    # Start compressing with parallel bzip
    cmd = 'tar -I lbzip2 -cvf ' + compressedRawDataName + ' scanSettings.mat *.yml *.txt *.ini ./rawData'
    print("\nRunning compression command: " + cmd + "\n")
    time.sleep(1)
    os.system(cmd)


if __name__ == "__main__":
    main()