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
import argparse
import re
from btpytools import tools, recipe
from brainreg.paths import Paths
from brainreg.main import main as register
from brainreg import cli
from imlib.general.numerical import check_positive_int


# Defaults for registration

DEFAULT_VOXEL_SIZE = 25
DEFAULT_CHANNEL = "red"
DEFAULT_ORIENTATION = "psl"
DEFAULT_ATLAS = "allen_mouse"


def main():

    # Parse input arguments
    args = get_arg_parser()
    args = args.parse_args()
    arg_groups = cli.get_arg_groups(args, cli.register_cli_parser())

    # Confirm that we are in a BakingTray acquisition directory that contains downsampled
    # stacks. Bail out if this is not the case.
    if not confirm_directory():
        return

    # Get the voxel size, providing a CLI UI if needed.
    (vox_size, ds_stacks_chosen_vox_size) = choose_vox_size(DEFAULT_VOXEL_SIZE, args)
    if ds_stacks_chosen_vox_size is False:
        return

    args.voxel_sizes = tuple([vox_size] * 3)  # set argument based on user choice

    # Get the color size, providing a CLI UI if needed.
    chosen_ds = choose_color_chan(DEFAULT_CHANNEL, args, ds_stacks_chosen_vox_size)
    if chosen_ds is False:
        return

    args.bt_channel = chosen_ds["channelname"]  # set argument based on user choice

    # Prepare variables for registration
    atlas_name = "%s_%dum" % (DEFAULT_ATLAS, args.bt_voxel)
    vol_to_register = chosen_ds["path2stack"]

    print(
        "\n\nRegistering data for sample %s with %d micron downsampled %s stack."
        % (chosen_ds["samplename"], vox_size, args.bt_channel)
    )

    input("Press return to start\n")

    # Make the directory/set the directory
    reg_dir = tools.make_reg_dir()
    args.brainreg_directory = Paths(reg_dir)

    # Run the registration using brainreg
    args, additional_images_downsample = cli.prep_registration(args)

    register(
        atlas_name,
        args.orientation,
        vol_to_register,
        args.brainreg_directory,
        args.voxel_sizes,
        arg_groups["NiftyReg registration backend options"],
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        backend=args.backend,
        debug=args.debug,
        save_original_orientation=args.save_original_orientation,
    )


def get_arg_parser():
    args = cli.register_cli_parser()

    # Add new options for BakingTray
    cli_args = args.add_argument_group("BakingTray data registration options")

    cli_args.add_argument(
        "-V",
        dest="bt_voxel",
        required=False,
        default=DEFAULT_VOXEL_SIZE,
        type=check_positive_int,
        help="Downsampled stack voxel size to register.",
    )

    cli_args.add_argument(
        "-C",
        "--channel",
        dest="bt_channel",
        required=False,
        default=DEFAULT_CHANNEL,
        type=str,
        help="Downsampled stack channel to register.",
    )

    cli_args.add_argument(
        "-D",
        "--use_defaults",
        dest="bt_use_defaults",
        required=False,
        action="store_true",
        help="If supplied, the CLI user choose is skipped and registration runs with defaults",
    )
    # Populate default values just in case this matters
    args.set_defaults(
        voxel_sizes=tuple([DEFAULT_VOXEL_SIZE] * 3),
        brainreg_directory=Paths(tools.ROOT_REG_DIR),
    )

    # Make these (and a few others) optional and also hide them from the help text
    # All the following will potentially need updating after the user has changed settings (TODO)
    for action in args._actions:
        if action.dest in [
            "voxel_sizes",
            "brainreg_directory",
            "image_paths",
            "downsample_images",
        ]:
            action.required = False
            action.help = argparse.SUPPRESS

    # Make orientation optional only (not invisiable) and set default
    for action in args._actions:
        if action.dest in [
            "orientation",
        ]:
            action.required = False

    args.set_defaults(orientation=DEFAULT_ORIENTATION)

    return args


def confirm_directory():
    """
    Confirm that we are in a BakingTray acquisition directory that contains downsampled
    stacks. Bail out if this is not the case.
    """

    if not tools.is_data_folder():
        print("\nCurrent folder is not a BakingTray acquisition directory\n")
        return False

    if not tools.has_downsampled_stacks():
        print("\nCurrent acquisition directory has no downsampled stacks\n")
        return False

    return True


def choose_vox_size(default, args):
    """
    Confirm that the desired voxel size exists. If the user
    has not changed the default value then we go through the a CLI
    interface to allow them to manually choose it or confirm it.
    """
    # Confirm that desired channel and voxel sizes exist

    ds_stacks = tools.available_downsampled_volumes()
    unique_voxel_sizes = list(set([x["voxelsize"] for x in ds_stacks]))

    # If the default voxel size matches that in the arg structure then
    # the user has not changed it. In this case we present the CLI UI
    if default == args.bt_voxel:
        run_cli_ui = True
    else:
        run_cli_ui = False

    # But if user supplies -D for using default values then this takes precedence and no UI
    if args.bt_use_defaults:
        run_cli_ui = False

    # Run the CLI UI
    msg = ""
    if run_cli_ui:

        msg = "Select downsampled stack voxel size for registration.\n(Enter a number and press return)\n"
        n = 1
        for t_vox in unique_voxel_sizes:
            msg += "%d. %d micron\n" % (n, t_vox)
            if default == t_vox:
                default_index = n - 1
            n += 1

        valid_answers = list(range(1, len(unique_voxel_sizes) + 1))
        valid_answers = [str(x) for x in valid_answers]
        error_str = "Enter a number between 1 and %d and press return" % (n - 1)
        reply = tools.cli_question(msg, valid_answers, default_index, error_str)

        chosen_voxel_size = unique_voxel_sizes[int(reply) - 1]
    else:
        chosen_voxel_size = args.bt_voxel

    ds_stacks_chosen_vox_size = [
        x for x in ds_stacks if x["voxelsize"] == chosen_voxel_size
    ]

    return (chosen_voxel_size, ds_stacks_chosen_vox_size)


def choose_color_chan(default, args, ds_stacks_chosen_vox_size):
    """
    Chose the desired channel from those available at the desired voxel size
    """

    # If the default channel matches that in the arg structure then
    # the user has not changed it. In this case we present the CLI UI
    if default == args.bt_channel:
        run_cli_ui = True
    else:
        run_cli_ui = False

    # But if user supplies -D for using default values then this takes precedence and no UI
    if args.bt_use_defaults:
        run_cli_ui = False

    # Run the CLI UI
    # These are the unique channel names
    chan_names = [x["channelname"] for x in ds_stacks_chosen_vox_size]

    msg = ""
    if run_cli_ui:
        msg = "Choose channel for registration.\n"
        n = 1
        for t_chan in chan_names:
            msg += "%d. %s channel\n" % (n, t_chan)
            if default == t_chan:
                default_index = n - 1
            n += 1

        valid_answers = list(range(1, len(chan_names) + 1))
        valid_answers = [str(x) for x in valid_answers]
        error_str = "Enter a number between 1 and %d and press return" % (n - 1)
        reply = tools.cli_question(msg, valid_answers, default_index, error_str)

        chosen_channel = chan_names[int(reply) - 1]
    else:
        chosen_channel = args.bt_channel

    # Extract dictionary element with this channel. There will be only one.
    chosen_ds = [
        x for x in ds_stacks_chosen_vox_size if x["channelname"] == chosen_channel
    ][0]

    return chosen_ds


if __name__ == "__main__":
    main()
