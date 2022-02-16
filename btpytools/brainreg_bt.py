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

import argparse
from btpytools import tools, recipe
from brainreg.paths import Paths
from brainreg.main import main as register
from brainreg import cli
from imlib.general.numerical import check_positive_int

# Default for registration
DEFAULT_VOXEL_SIZE = 50
DEFAULT_CHANNEL = "red"
DEFAULT_ORIENTATION = "psl"
DEFAULT_ATLAS = "allen_mouse"

voxel_size = tuple([DEFAULT_VOXEL_SIZE] * 3)
paths = Paths("OUTTEST")


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
    # Set defaults manually

    args.set_defaults(
        voxel_sizes=voxel_size,
        orientation=DEFAULT_ORIENTATION,
        brainreg_directory=paths,
    )

    # Make these (and a few others) optional and also hide them from the help text
    for action in args._actions:
        if action.dest in [
            "voxel_sizes",
            "brainreg_directory",
            "image_paths",
            "downsample_images",
        ]:
            action.required = False
            action.help = argparse.SUPPRESS

    # Make optional only
    for action in args._actions:
        if action.dest in [
            "orientation",
        ]:
            action.required = False

    return args


def main():

    args = get_arg_parser()
    args = args.parse_args()
    arg_groups = cli.get_arg_groups(args, cli.register_cli_parser())

    args, additional_images_downsample = cli.prep_registration(args)

    if not tools.is_data_folder():
        print("\nCurrent folder is not a BakingTray acquisition directory\n")
        return

    if not tools.has_downsampled_stacks():
        print("\nCurrent acquisition directory has no downsampled stacks\n")
        return

    ds_stacks = tools.available_downsampled_volumes()

    unique_voxel_sizes = list(set([x["voxelsize"] for x in ds_stacks]))

    # User chooses voxel size
    if not args.bt_voxel in unique_voxel_sizes:
        print("No %d micron voxel size available. Available sizes are:" % args.bt_voxel)
        [print("%d micron" % v) for v in unique_voxel_sizes]
        return

    # Todo - following is just to make sure stuff works.
    ds_stacks_chosen_vox_size = [
        x for x in ds_stacks if x["voxelsize"] == args.bt_voxel
    ]

    chan_names = [x["channelname"] for x in ds_stacks_chosen_vox_size]

    if not args.bt_channel in chan_names:
        # Bail out if channel can not be found
        print("No %s channel not available. Available channels are:" % args.bt_channel)
        [print(c) for c in chan_names]
        return

    # Extract dictionary element with this channel. There will be only one.
    chosen_ds = [
        x for x in ds_stacks_chosen_vox_size if x["channelname"] == args.bt_channel
    ][0]

    # Prepare variables for registration
    atlas_name = "%s_%dum" % (DEFAULT_ATLAS, args.bt_voxel)
    vol_to_register = chosen_ds["path2stack"]

    print("Registering data for sample %s" % chosen_ds["samplename"])
    print(
        "Registering %d micron downsampled %s stack" % (args.bt_voxel, args.bt_channel)
    )

    input("Press return to start")

    register(
        atlas_name,
        args.orientation,
        vol_to_register,
        paths,
        args.voxel_sizes,
        arg_groups["NiftyReg registration backend options"],
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        backend=args.backend,
        debug=args.debug,
        save_original_orientation=args.save_original_orientation,
    )


if __name__ == "__main__":
    main()
