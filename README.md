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
