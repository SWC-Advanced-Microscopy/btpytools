#!/usr/bin/env python3

""" Transfer raw data to server

This function is a wrapper round rsync and is used for copying BakingTray
data to a server over a network connection. It corrects trailing slash 
issues. It doesn't currently support rsync over ssh.

Inputs arguments
- one or more paths to local directories which are to be copied
- the last path is the destination. 

transferToServer ./localSampleA ./localSampleB /path/to/server

Advanced input arguments
- You may add a custom rsync switch. By default -av is used. But you may,
  for example, do a dry run by supplying -avn. This can be supplied either
  before or after the directory paths (see example below)

 Usage examples:

 1. Transfer one sample
 transferToServer ./XY_123 /mnt/datastor/user/path/

 2. Transfer two samples in same directory plus raw data
    This usage case happens if a sample was split up
 transferToServer ./XY_123_YY_234/sample1 ./XY_123_YY_234/sample2 ./XY_123_YY_234/rawData.tar.bz /mnt/datastor/user/path/

 You can also do:
 transferToServer ./XY_123_YY_234/ /mnt/datastor/user/path/

 The latter will ask you if you want the data copied in the enclosing directory.

 3. Change rsync flag (advanced usage) using either of the following
 transferToServer -rv ./XY_123 /mnt/datastor/user/path/
 transferToServer ./XY_123 /mnt/datastor/user/path/ -rv

Notes
If you have signed in via SSH and aren't in a tmux session, the function
asks for confirmation before continuing. If your ssh session breaks off
for some reason, then compression will fail. tmux is therefore recomended
in this situation.

"""


import os
import sys
from btpytools import tools, recipe



def main():
    # Search for an rsync switch string and replace default value if one is found
    main_rsync_switch='-av' # default
    for ii, jj in enumerate(sys.argv):
        if jj.startswith('-'):
            main_rsync_switch=jj
            sys.argv.remove(jj)


    # Need to supply at least what to copy and where to copy it to 
    if len(sys.argv)<3:
        print("Supply at least a local path to copy and a destination")
        exit()



    source  = sys.argv[1:-1]   # One or more files or folders to copy
    destination = sys.argv[-1] # Where we will copy to


    # Bail out if any of the supplied paths do not exist
    fail=False;
    for tPath in source:
        if not os.path.exists(tPath):
            print("%s does not exist" % tPath)
            fail=True


    # At least check if the targtet location is a directory
    if not os.path.isdir(destination):
        print("%s is not a valid destination directory" % destination)
        fail=True

    if fail:
        exit()


    # Remove trailing slash from data directories that don't contain data sub-directories
    for ii,tDir in enumerate(source):
        if tools.is_data_folder(tDir) and not tools.contains_data_folders(tDir):
            # If here, tDIR is a sample folder without sub-folders. If there is a 
            # trailing slash then we should delete it. Always. 
            if tDir[-1] == os.path.sep:
                source[ii] = tDir[0:-1]

        elif tools.contains_data_folders(tDir):
            # If here, tDIR contains sub-folders which are sample folders is a sample folder without sub-folders
            # We again delete the trailing slash but we give the user the option to add it back
            if tDir[-1] == os.path.sep:
                source[ii] = tDir[0:-1]
            print("\nDirectory \"%s\" contains multiple samples." % tDir)
            print("Do you want to keep samples in their enclosing directory (%s) when on the server?" % tDir)
            if not tools.query_yes_no(''):
                source[ii] = source[ii] + os.path.sep

    print("")


    # Check whether any of the directories we plan to copy already exist at the destination
    safeToCopy=True
    for ii,tDir in enumerate(source):

        if tDir[-1] != os.path.sep:
            # Look for this directory at the destination
            destinationPath = os.path.join(destination,tDir)
            if os.path.exists(destinationPath):
                safeToCopy=False
                print("===>>> WARNING!! \"%s\" already exists in \"%s\"!! Proceeding will over-write its contents <====" % (tDir,destination))
        else:
            # Look for the *contents* of this directory at the destination
            dirContents = os.listdir(tDir);
            for jj,subDir in enumerate(dirContents):
                if subDir == 'rawData' or '_DELETE_ME' in subDir:
                    continue
                destinationPath = os.path.join(destination,subDir)
                if os.path.exists(destinationPath):
                    safeToCopy=False
                    print("===>>> WARNING!! \"%s\" already exists in \"%s\"!! Proceeding will over-write its contents <====" % (subDir,destination))

    if safeToCopy==False:
        print("\n IS IT OK TO PROCEED DESPITE THE ABOVE WARNINGS?")
        if not tools.query_yes_no(''):
            exit()




    #Ask for confirmation before starting
    print("\nPerform the following transfer?")
    for ii,tDir in enumerate(source):
        if tDir[-1] != os.path.sep:
            print("Copy directory \"%s\" to location \"%s\"" % (tDir,destination))
        else:
            dirContents = os.listdir(tDir);
            for jj,subContents in enumerate(dirContents):
                if subContents=='rawData' or subContents.endswith('_DELETE_ME'):
                    pass
                else:
                    print("Copy \"%s\" to \"%s\"" % (subContents,destination))



    cmd = ('rsync %s --progress --exclude rawData --exclude *_DELETE_ME_* %s %s ' % 
              (main_rsync_switch, " ".join(source),destination) )

    print("Using command %s" % cmd)
    if not tools.query_yes_no(''):
        exit()

    # Start the transfer
    os.system(cmd)


if __name__ == "__main__":
    main()
