#Introduction and motivation

When working on the command line such as in the Bash shell, applications
support command line flags and parameters.  It is quite convenient to
interact with programs using options and flags that can be specified in
any order, e.g.,
```
$ my_appl  -N 10  -alpha 1.3
```
could be specified equivalently as,
```
$ my_appl  -alpha 1.3  -N 10
```

Many programming languages offer support to conveniently deal with
command line arguments out of the box, e.g., Python.  However, many
languages used in a scientific context don't, e.g., C/C++, Fortran,
R, and Matlab.
Although those languages offer the necessary facilities, it is at best
somewhat cumbersome to use them, and often the process is rather error
prone.  A similar picture emerges when a programmer has to deal with
configuration files, again, a painstaking process.

Quite a number of libraries have been developed over the years that can be
used to conveniently handle command line arguments and configuration files.
However, this complicates the deployment of the application since it will
have to rely on the presence of these libraries.

ParameterWeaver has a different approach: it generates the necessary code
to deal with the command line arguments and configuration files of the
application in the target language, so that these source files can be
distributed along with those of the application.  This implies that systems
that do not have ParameterWeaver installed still can run that application.

Using ParameterWeaver is as simple as writing a definition file for the
command line arguments and/or configuration parameters, and executing the
code generator via the command lnie.  This can be conveniently integrated
into a standard build process such as make.

ParameterWeaver currently supports the following target languages:

  * C/C++
  * Fortran
  * R
