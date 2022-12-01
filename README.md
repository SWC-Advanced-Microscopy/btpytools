# StitchIt Python Tools

The directory contains Python code for managing BakingTray serial-section 2p data.
The main functions of interest are `compressRawData.py` and `transferToServer.py`, which are aimed at end users of the microscope. 
The `recipe.py` and `tools.py` modules support these and are aimed at developers. 



## Install instructions
If you wish to use the data management tools and do not care about the `brainreg` helper tool:
```
$ pip install btpytools

```

You will then be able to run the following commands at the system command prompt:


* `transferToServer`
* `compressRawData`
* `summariseAcqs`

If you also want the `brainreg` helper command `brainregbt` (see below) then install with 
```
$ pip install btpytools[register]

```
This will also install brainreg and all of its dependencies, which are many. 

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

**NOTE**: If `RC_RabiesBrains01`  contains a compressed raw data archive, the following will **not** transfer it:
```
$ transferToServer RC_RabiesBrains01/sample01 RC_RabiesBrains01/sample02 /mnt/server/user/data/histology
```


### Wrapper for brainreg with BakingTray data
With this package installed and also brainreg installed you can run registrations with super easily at the command line using the downsampled stacks generated by StitchIt.

* `cd` to a BakingTray sample directory
* Run `brainregbt`


Sample session
```
$ brainregbt
Select downsampled stack voxel size for registration.
(Enter a number and press return)
1. 25 micron
2. 50 micron

[1] ?
Choose channel for registration.
1. red channel
2. green channel

[1] ?


Registering data for sample SM_1099839 with 50 micron downsampled red stack.
Press return to start
```

Running `brainregbt -D` will run the registration with the above defaults. Available resolutions depend on which downsampled stacks were generated by StitchIt.



### To build on Apple Silicon
First do:

```
pip install cython
brew install hdf5 c-blosc
export HDF5_DIR=/opt/homebrew/opt/hdf5 
export BLOSC_DIR=/opt/homebrew/opt/c-blosc
```