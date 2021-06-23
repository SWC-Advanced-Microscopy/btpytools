#!/usr/bin/env python3

""" Sumarise to screen all acquisitions in the current dirctory

Usage
cd to sample directory and run this command:
$ cd /mnt/data/
$ summariseAcquisitions

"""

import os

from btutils import tools, recipe


dirs = next(os.walk('.'))[1]

for tDir in dirs:

    if tools.is_data_folder(tDir):
        print('%s is a BakingTray Acq started at %s' % (tDir,recipe.acq_start_time(tDir)))
    elif tools.contains_data_folders(tDir):
        print('%s contains BakingTray Acq sub-dirs' % tDir)
    else:
        print('%s is not a BakingTray acq dir' % tDir)

