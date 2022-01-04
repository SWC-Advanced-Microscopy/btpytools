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


Runs much faster with parallel bzip (lbzip2) installed. If this is missing, the tool reverts
to regular gzip.

"""

import os
from datetime import datetime
import time
from btpytools import tools, recipe
from glob import glob

def main(simulate=False):

    if simulate:
        print('\n\nRUNNING IN SIMULATE MODE\n')


    if tools.has_raw_data() == False:
        print("No rawData folder found in", os.getcwd())
        exit()


    # The sample ID is used to name the raw data directory. We get this information from
    # the recipe file. We look for this in the current directory and, failing that, in the
    # cropped data directory. If neither exists, we use the current directory name instead. 

    # If there is no recipe file in the current directory, look for one in the cropped data dir. 
    # if also that is missing, we use as the 

    copy_files_from_uncropped = False # Do we need to temporarily copy settings files out of the uncropped data dir?

    if tools.has_recipe_file():
        sample_name = recipe.sample_id()
    elif tools.has_uncropped_stitched_images():
        # Can we get sample ID from a recipe file in the uncropped stacks directory?
        uncropped_dir = glob(tools._uncropped_wildcard)[0]
        if tools.has_recipe_file(uncropped_dir):
            # We get the sample ID from the uncropped data directory, so we also want to later
            # copy other settings files temporarily into the current directory so they
            # get archived
            print('Getting sample information from meta-data files in uncropped data directory')
            copy_files_from_uncropped = True
            sample_name = recipe.sample_id(uncropped_dir)
        else:
            # We find no recipe file anywhere but there were were raw data. Let's, therefore,
            # use the current working directory and the date to build the sample name
            print('No meta data files. Making up a sample ID from directory name.')
            cwd = os.getcwd()
            sample_name = cwd.split(cwd[0])[-1]

            now = datetime.now()
            sample_name  = sample_name + now.strftime('_%Y%m%d')




    print("Found rawData directory for sample " + sample_name)


    # Begin compression, but warn if we aren't in a tmux session if this is an SSH connection
    if tools.in_ssh_session() and not tools.in_tmux_session():
        if not tools.query_yes_no("\nYou are logged in via SSH but are not in a tmux session, proceed anyway?","no"):
            print("Not proceeding with compression.\n")
            exit()


    # We will also copy metadata
    meta_data_file_names = 'scanSettings.mat *.yml *.txt *.ini' # wildcards for files other than raw data that we will compress 


    # Check whether we have lbzip2 and use it if so
    out = os.system('lbzip2 -h > /dev/null')
    has_lbzip2 = out==0

    if has_lbzip2:
        tar_switches = '-I lbzip2 -cvf'
        compressed_rawdata_name = sample_name + "_rawData.tar.bz"

    else:
        tar_switches = '-zcvf'
        compressed_rawdata_name = sample_name + "_rawData.tar.gz"
        print('\n\n** WARNING -- parallel compression tool lbzip2 not found. Using much slower single-threaded gzip.\n\n')
        time.sleep(3)

    # Start compressing with parallel bzip
    compress_cmd = 'tar %s %s %s ./rawData ' % (tar_switches, compressed_rawdata_name, meta_data_file_names)

    print("\nRunning compression command: " + compress_cmd + "\n")
    time.sleep(1)

    if not simulate:
        # If necessary we copy the meta-data files temporaily out of the uncropped stacks folder
        if copy_files_from_uncropped:
            print('Temporarily moving meta-data from uncropped directory into main directory')
            for these_files in meta_data_file_names.split(' '):
                os.system('cp %s/%s ./' % (uncropped_dir,these_files))

        # Run the compression command
        os.system(compress_cmd)

        # If needed, remove the files that we added. The following is slightly dangerous, but if normal
        # usage there should be no problem with the wild card delete. 

        if copy_files_from_uncropped:
            print('\nTidying up temporarily copied files')
            os.system('rm -f %s' % meta_data_file_names)



if __name__ == "__main__":
    main()
