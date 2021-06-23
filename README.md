# StitchIt Python Tools

The directory contains Python code for managing BakingTray serial-section 2p data.
The main functions of interest are `compressRawData.py` and `transferToServer.py`, which are aimed at end users of the microscope. 
The `recipe.py` and `tools.py` modules support these and are aimed at developers. 



## Install instructions
* pip install -r requirements.txt
* Create a directory for your Python code. e.g. ~/myPythonStuff
* Add it to the Python path. e.g. `export PYTHONPATH=/opt/stitchit/python_tools/src:$PYTHONPATH`
* Symlink or copy the btutils folder into here.
* Create symlinks to functions you wish to have access to such that they are in your system path. e.g. you can symlink transferToServer.py to `/usr/local/bin/transferToServer`

