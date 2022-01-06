#!/usr/bin/env python3

""" Summarize to screen all acquisitions in the current directory

Usage
cd to sample directory and run this command:
$ cd /mnt/data/
$ summariseAcquisitions

This function is automatically added as a console-accessible command during pip install
"""


import os

from btpytools import tools, recipe


def main():
    dirs = next(os.walk("."))[1]

    for tDir in dirs:

        if tools.is_data_folder(tDir):
            print(
                "%s is a BakingTray Acq started at %s"
                % (tDir, recipe.acq_start_time(tDir))
            )
        elif tools.contains_data_folders(tDir):
            print("%s contains BakingTray Acq sub-dirs" % tDir)
        else:
            print("%s is not a BakingTray acq dir" % tDir)


if __name__ == "__main__":
    main()
