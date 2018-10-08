---
description: >-
  This document will go through my setup for linux kernel code navigation using
  YCMD for Emacs.
---

# emacs-ycmd Linux Kernel

## Building YCMD and fetching its dependencies

Cloned YCMD from its official github page and built it. I had to upgrade my cmake and install libpython 3.

### cmake 3

Make sure you have `cmake --version` report at least version 3. Or you can update as follows:

```bash
sudo apt-get remove cmake
sudo apt-get update
sudo apt-get install cmake3
```

### Install libpython3.4-dev

My build of YCMD reported this error and I fixed it by installing libpython3.4-dev`Searching Python 3.4 libraries... ERROR: Python headers are missing in /usr/include/python3.4m`

```bash
sudo apt-get install libpython3.4-dev
```

### Build Command:

```bash
ycmd_repo$ python3 ./build.py --clang-completer --build-dir ./build_tree/
```

## Installing emacs-ycmd client

Emacs has this client which interacts with YCMD. More details in [https://github.com/abingham/emacs-ycmd](https://github.com/abingham/emacs-ycmd).

This is the configuration used for the emacs plugin in file `init.el`:

```scheme
(require 'ycmd)
(require 'company)
(require 'company-ycmd)
(add-hook 'after-init-hook #'global-ycmd-mode)
(set-variable 'ycmd-server-command `("python3",  (file-truename  "<path to ycmd repo>/ycmd>")))
(set-variable 'ycmd-extra-conf-handler 'load)
(company-ycmd-setup)
(setq company-idle-delay 0.2)
(eval-after-load 'cc-mode '(define-key c-mode-base-map (kbd "M-.") (function ycmd-goto)))
(global-ycmd-mode)

```

## Generate compilation database for linux kernel using Bear

Since ycmd is based on clang tools, it needs a compilation database to work \(or at least compilation flags for each file to parse your code\). More information can be found at: [https://github.com/Valloric/YouCompleteMe\#c-family-semantic-completion](https://github.com/Valloric/YouCompleteMe#c-family-semantic-completion)

Build tools like bazel and cmake have options to generate this compilation database \(which is a json file named  compile\_commands.json\). But linux kernel uses GNU make for its build. There is a tool called [Bear](https://github.com/rizsotto/Bear) which can be used to generate compilation database from GNU make by intercepting compilation calls.

I compiled linux kernel using `defconfig` config. And then used Bear to intercept the compilation calls:

```bash
linux-repo$ make defconfig
linux-repo$ <path/to/bear>/bin/bear -l <path/to/bear>/bin/lib/x86_64-linux-gnu/bear/libear.so make
```

After running this command and waiting for a few minutes depending on how many CPU cores you had to build, you'll find \`compile\_commands.json\` at the root of the kernel repo.

Now launching Emacs to browse the kernel and say opening `fork.c` and pressing `M-.` on a function or symbol will navigate to the function or symbol.  However using this setup I could not navigate symbols inside a header file. Eg. search for `slab.h` and try pressing `M-.` on symbols on it did not work.

## Root causing why M-. in some header files did not work

Turns out when using a compilation database, ycmd tries to get flags for header files as per the following rule \(defined in[ ycmd's page](https://github.com/Valloric/YouCompleteMe#option-1-use-a-compilation-database)\):

_If the file is a header file and a source file with the same root exists in the database, the flags for the source file are used. For example, if the file is /home/Test/project/src/lib/something.h and the database contains an entry for /home/Test/project/src/lib/something.cc, then the flags for /home/Test/project/src/lib/something.cc are used.  
Otherwise, if any flags have been returned from the directory containing the requested file, those flags are used. This heuristic is intended to provide potentially working flags for newly created files._

In the kernel, there are some directories where there are only header files and it means that those header files won't get any compilation flags preventing ycmd from parsing those and thus we cannot navigate symbols in it.

## Making header file navigation work

ycmd optionally allows users to define compilation flags for each files in the source tree by adding a file named `.ycm_extra_conf.py` in the project root. I added a custom [https://github.com/sujankh/emacs-ycmd-linuxkernel/blob/master/.ycm\_extra\_conf.py](https://github.com/sujankh/emacs-ycmd-linuxkernel/blob/master/.ycm_extra_conf.py) in my linux kernel root directory and this fixed the problem. Here is what the file does \(the code is commented as well\):

* I curated the default `flags` variable by looking at one entry in the generated `compile_commands.json` file and removing file-name specific options.
* Updated `Settings` function to return those default flags if the compilation database did not have an entry for the file. This made sure those header files \(which did not have any source files as siblings\) got a compilation flag making navigation possible.

[https://github.com/Valloric/YouCompleteMe\#option-2-provide-the-flags-manually](https://github.com/Valloric/YouCompleteMe#option-2-provide-the-flags-manually) has more details on how the `.ycm_extra_conf.py` file works. 

