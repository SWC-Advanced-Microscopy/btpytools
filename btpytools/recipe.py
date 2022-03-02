"""
Tools for handling BakingTray recipe files
"""

import os
import yaml

from glob import glob
from btpytools import tools


def read_recipe(dirToSearch=""):
    """Read recipe file from current directory or a defined directory.
    If multiple files present, reads the last one
    Return False if no recipe present
    """
    if len(dirToSearch) == 0:
        dirToSearch = os.getcwd()

    if tools.has_recipe_file(dirToSearch) == False:
        print("No recipe file found in", dirToSearch)
        return 0

    with open(glob(os.path.join(dirToSearch, "recipe*.yml"))[-1], "r") as stream:
        try:
            recipe = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Failed to read recipe file")
            print(exc)
            return False

    return recipe


def sample_id(dirToSearch=""):
    """return sample ID as a string"""
    this_recipe = read_recipe(dirToSearch)
    if not this_recipe:
        return False
    else:
        return this_recipe["sample"]["ID"]


def microscope(dirToSearch=""):
    """return microscope name as a string"""
    this_recipe = read_recipe(dirToSearch)
    if not this_recipe:
        return False
    else:
        return this_recipe["SYSTEM"]["ID"]


def acq_start_time(dirToSearch=""):
    """return acquisition start time as a string"""
    this_recipe = read_recipe(dirToSearch)
    if not this_recipe:
        return False
    else:
        return this_recipe["Acquisition"]["acqStartTime"]
