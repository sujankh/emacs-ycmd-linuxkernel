Using Emacs YCMD to navigate Linux Kernel
============================================================
[Work in Progress]
This document will go through my setup for linux kernel code navigation using YCMD for Emacs.

Building YCMD
------------------------------------------------------------
Cloned YCMD from its official github page and built it:


Dependencies:
-------------------------------------------------------------

##### cmake3
Make sure you have `cmake --version` report at least version 3.
Or you can update as follows:
```
sudo apt-get remove cmake
sudo apt-get update
sudo apt-get install cmake3
```

##### Install libpython3.4-dev
My build of YCMD reported this error
```Searching Python 3.4 libraries...
ERROR: Python headers are missing in /usr/include/python3.4m.
```

I had to install development version of python 3
```bash
sudo apt-get install libpython3.4-dev
```

##### Build:
```
ycmd_repo$ python3 ./build.py --clang-completer --build-dir ./build_tree/
```
