#High-level overview &amp; concepts

##Parameter definition files

A parameter definition file is a CSV text file where each line defines a
parameter.  A parameter has a type, a name, a default values, and
optionally, a description.  To add documentation, comments can be added to
the definition file.  The types are specific to the target language, e.g.,
an integer would be denoted by `int` for C/C++, and by `integer` for
Fortran 90.  The supported types are documented for each implemented
target language.

By way of illustration, a parameter definition file is given below for C
as a target language, additional examples are shown in the target language
specific sections:
```
int,numParticles,1000,number of particles in the system
double,temperature,273,system temperature in Kelvin
char*,intMethod,'newton',integration method to use
```
Note that this parameter definition file should be viewed as an integral
part of the source code.

##Code generation

ParameterWeaver will generate code to

  * initialize the parameter varaibles to the default values as specified in
    the parameter definition file;
  * parse the actual command line arguments at runtime to determine the user
    specified values, and
  * optionally, parse a configuration file;
  * print the values of the parameters to an output stream.

The implementation and features of the resulting code fragments are
specific to the target language, and try to be as close as possible to the
idioms of that language.  Again, this is documented for each target
language specifically.  The nature and number of these code fragments
varies from one target language to the other, again trying to match the
language's idioms as closely as possible.  For C/C++, a declaration file
(`.h`) and a definition file (`.c`),  as well as a source and header file
containing definitions and declarations of auxillary functions.  For
Fortran 90, a single file (`.f90`) will be generated that contains
both declarations and definitions.
