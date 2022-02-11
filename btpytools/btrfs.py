import os
import re

"""
Simple tools for assisting with troublehooting btrfs RAID arrays.
Not bulletproof!

must install smartmontools and btrfs-progs
"""


def return_mount_point():
    """
    Assumes fstab has one btrfs mount point and returns the path to this.

    Inputs
    none

    Outputs
    A string corresponding to the btrfs mouint pount
    """
    with open("/etc/fstab", "r") as stream:
        contents = stream.read()
        match = re.search(r" +(/.*? ) +btrfs +", contents)
        return match.group(1)


def show(quiet=False, verbose=False):
    """
    Run btrfs fi show on btrfs array. By default print to screen the standard output from
    the command.
    """
    cmd = "sudo btrfs fi show %s" % return_mount_point()
    if verbose:
        os.system(cmd)
    std_out = os.popen(cmd).read()

    if not quiet:
        print(std_out)

    return std_out


def return_hdds_as_list():
    """
    Return btrfs devices on array as a list of strings
    """
    txt = show(quiet=True)
    match = re.findall("/dev/.*", txt)
    return match


def power_on_time(quiet=False):
    """
    Power on time of each device in the array
    """
    hdds = return_hdds_as_list()
    power_on_days = list()
    for t_hdd in hdds:
        cmd = "sudo smartctl --all %s | grep Power_On_Hours" % t_hdd
        std_out = os.popen(cmd).read()
        match = re.match(r".*- + (\d+)", std_out)

        power_on_days.append(int(match.group(1)) / 24)

        if not quiet:
            print("%s %d days" % (t_hdd, int(power_on_days[-1])))

    return (hdds, power_on_days)


def disks_older_than(threshold_age=700):
    """
    Print to screen a list of disks older than a certain number of days.
    By default 700 days is the threshold.

    Inputs
    threhold_age - scalar defining the number of days older than which we print
                  the disk name
    """

    disk_data = power_on_time(quiet=True)

    for t_disk in zip(disk_data[0], disk_data[1]):
        if t_disk[1] > threshold_age:
            print("%s %d days" % (t_disk[0], int(t_disk[1])))
