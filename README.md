# StitchIt Python Tools

The directory contains Python code for managing BakingTray serial-section 2p data.
The main functions of interest are `compressRawData.py` and `transferToServer.py`, which are aimed at end users of the microscope. 
The `recipe.py` and `tools.py` modules support these and are aimed at developers. 



## Install instructions
```
$ sudo pip install btpytools

```

Running as `sudo` allows the installer to add the most important programs to your path, allowing them to be run at the system command line:


* `transferToServer`
* `compressRawData`
* `summariseAcqs`

In other words, after pip installing you can run `compressRawData` at the command line. 

## Usage instructions

### Compressing the raw data directory
`cd` to the sample directory at the command line and run `compressRawData`. This works much faster
if you to have installed `lbzip2`, which runs parallel bzip. Likely only works on Linux. The
command also confirms there is enough disk space available to complete successfully.

```
$ cd /mnt/data/BakingTrayStacks/CC_125_1__125_2/ 
$ compressRawData  
```

### Sending data to a remote server
The server should be mounted locally to a mount point writable by the user. The tranfer is via `rsync`. The command just ensures no uncompressed raw data or uncropped stacks are copied. It brute-force retries if there is a failure for some reason. 

First `cd` to the directory which **contains your samples**. Not the sample directory. e.g.
```
$ cd /mnt/data/BakingTrayStacks
```

You can now run in either of the following two ways (either one acquisition or multiple acquisitions)
```
$ transferToServer RC_RabiesBrains01 /mnt/server/user/data/histology
$ transferToServer RC_RabiesBrains01 RC_TwoProbeTracks_test RC_MyOldSample /mnt/server/user/data/histology
```

Do **not** do the following as it will not send compressed raw data should you have any:
```
$ transferToServer RC_RabiesBrains01/sample01 RC_RabiesBrains01/sample02 /mnt/server/user/data/histology
```
