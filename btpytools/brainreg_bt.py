#!/usr/bin/env python3

""" Run brainreg on a BakingTray acquisition

Assumes the brain was acquired such that the images stacks are orderd posterior to anterior
and the dorsal surface is at the top of the images


Usage
cd to sample directory and run this command:
$ cd /mnt/data/
$ brainreg_bt

This function is automatically added as a console-accessible command during pip install
"""

import os

from btpytools import tools, recipe
from brainreg.main import main as register
from brainreg.paths import Paths


paths = Paths("OUTTEST")


def main():
    register("allen_mouse_25um", "psl", "ch3m.tif", paths, (25, 25, 25), None)


if __name__ == "__main__":
    main()
