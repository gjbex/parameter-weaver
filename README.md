parameter-weaver
================

Code generator for dealing with command line arguments and configuration files

What is it?
-----------

ParameterWeaver is a code generator to handle command line parameters
and configuration files for C/C++/Fortran/R/Octave

Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.



Prerequistes
------------

To install ParameterWeaver, you will need GNU make, which comes with
almost any Linux or Unix distribution.  To run ParameterWeaver, you will
need the Bash shell (although an equivalent shell script for a Csh-ish
shell is easy to write), as well as a Python 2 distribution, Python 2.6.x
or later.



Installation
------------

The make file in the src directory will perform the installation.
By default, it will install in /usr/local, but you can override this,
see below.  So:
```
$ ./configure
$ make install
```

This will add a wrapper script weave to /usr/local/bin, and a directory
parameter-weaver to /usr/local/lib.  It will also add a directory with
the same name to /usr/local/doc and /usr/local/examples, creating those
directories if they do not already exist.

If you would llke to install in another directory, use:
```
$ ./configure --prefix=<your-apps-dir>
$ make install
```


Documentation
-------------

Help can be obtained using the help flag:
```
$ weave -h
```
Documentation in HTML format is installed in doc/parameter-weaver in the
installation directory.  Examples can be found in examples/parameter-weaver.
The latter also show how to use ParameterWeaver in conjunction with make.



Bugs, issues, feature requests
------------------------------

Please contact the author, Geert Jan BEX <geertjan.bex@uhasselt.be>.

