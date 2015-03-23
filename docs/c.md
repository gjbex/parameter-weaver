#C/C++ documentation

##Data types

For C/C++, ParameterWeaver supports the following data types:

  * `int`
  * `long`
  * `float`
  * `double`
  * `bool`
  * `char *`

##Example C program

Suppose we want to pass command line parameters to the following C program:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    FILE *fp;
    int i;
    if (strlen(out) &gt; 0) {
        fp = fopen(out, "w");
    } else {
        fp = stdout;
    }
    if (verbose) {
        fprintf(fp, "# n = %d\n", n);
        fprintf(fp, "# alpha = %.16f\n", alpha);
        fprintf(fp, "# out = '%s'\n", out);
        fprintf(fp, "# verbose = %s\n", verbose);
    }
    for (i = 0; i &lt; n; i++) {
        fprintf(fp, "%d\t%f\n", i, i*alpha);
    }
    if (fp != stdout) {
        fclose(fp);
    }
    return EXIT_SUCCESS;
}
```

We would like to set the number of iterations `n`, the factor `alpha`, the
name of the file to write the output to `out` and the verbosity `verbose`
at runtime, i.e., without modifying the source code of this program.

Moreover, the code to print the values of the variables is error prone, if
we later add or remove a parameter, this part of the code has to be updated
as well.

Defining the command line parameters in a parameter definition file to
automatlically generate the necessary code simplifies matters considerably.

##Example parameter definition file

The following file defines four command line parameters named `n`, `alpha`,
`out` and `verbose`.  They are to be interpreted as `int`, `double`, `char`
pointer and `bool` respectively, and if no values are passed via the
command line, they will have the default values `10`, `0.19`, `output.txt`
and false respectively.  Note that a string default value is quoted.  In
this case, the columns in the file are separated by tab characters.  The
following is the contents of the parameter definition file `param_defs.txt`:
```
int	n	10
double	alpha	0.19
char *	out	'output.txt'
bool	verbose	false
```

This parameter definition file can be created in a text editor such as the
one used to write C program, or from a Microsoft Excel worksheet by saving
the latter as a CSV file.

As mentioned above, boolean values are also supported, however, the
semantics is slightly different from other data types.  The default value
of a logical variable is always false, regardless of what is specified in
the parameter definition file.  As opposed to parameters of other types, a
logical parameter acts like a flag, i.e., it is a command line options that
doesn't take a value.  Its absence is interpreted as false, its presence as
true.  Also note that using a parameter of type `bool` implies that
the program will have to be complied as C99, rather than C89.  All modern
cmopiler fully support C99, so that should not be an issue.  However, if
your program needs to adhere strictly to the C89 standard, simply use a
parameter of type `int` instead, with `0` interpreted as
false, all other values as true.  In that case, the option takes a value
on the command line.

##Generating code

Generating the code fragments is now very easy.  If appropriate, load the
module (thinking):
```
$ module load parameter-weaver
```
Next, we generate the code based on the parameter definition file:
```
$ weave -l C -d param_defs.txt
```
A number of type declarations and functions are generated, the declarations
in the header file `cl_params.h`, the defintions in the source file
`cl_params.c`.

  * data structure: a type `Params` is defined as a `typedef` of a `struct`
    with the parameters as fields, e.g.,
    ```
    typedef struct {
        int n;
        double alpha;
        char *out;
        bool verbose;
    } Params;
    ```
  * Initialization function: the default values of the command line
    parameters are assigned to the fields of the `Params` variable,
    the address of which is passed to the function.
  * Parsing: the options passed to the program via the command line are
    assigned to the appropriate fields of the `Params` variable.  Moreover,
    the `argv` array containing the remaining command line
    arguments, the `argc` variable is set apprppriately.
  * Dumper: a function is defined that takes three arguments: a file
    pointer, a prefix and the address of a `Params` variable.  This
    function writes the values of the command line parameters to the file
    pointer, each on a separate line, preceeded by the specified prefix.
  * Finalizer: a function that deallocates memory allocated in the
    initialization or the parsing functions to avoid memory leaks.

##Using the code fragments

The declarations are simply included using preprocessor directives:
```
  #include "cl_parser.r"
```
A variable to hold the parameters has to be defined and its values initialized:
```
  Params params;
  initCL(&params);
```
Next, the command line parameters are parsed and their values assigned:
```
  parseCL(&params, &argc, &argv);
```
The dumper can be called whenever the user likes, e.g.,
```
  dumpCL(stdout, "", &params);
```
The code for the program is thus modified as follows:
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cl_params.h"

int main(int argc, char *argv[]) {
    FILE *fp;
    int i;
    Params params;
    initCL(&params);
    parseCL(&params, &argc, &argv);
    if (strlen(params.out) &gt; 0) {
        fp = fopen(params.out, "w");
    } else {
        fp = stdout;
    }
    if (params.verbose) {
        dumpCL(fp, "# ", &params);
    }
    for (i = 0; i &lt; params.n; i++) {
        fprintf(fp, "%d\t%f\n", i, i*params.alpha);
    }
    if (fp != stdout) {
        fclose(fp);
    }
    finalizeCL(&params);
    return EXIT_SUCCESS;
}
```
Note that in this example, additional command line parameters are simply
ignored.  As mentioned before, they are available in the array `argv`,
`argv[0]` will hold the programs name, subsequent elements up to
`argc - 1` contain the remaining command line parameters.

##Using a configuration file

parameter-weaver generates a function from the same parameter definition
file to parse a configuration file, in addition to command line parameters.
The format of the configuration file, e.g., `config-03.txt` is very
straightforward, as the example below illustrates.
```
alpha = 0.19
# comments can be added, as can blank lines
out = 'output-03.txt'

verbose = true
```
Comment lines start with a `#`, and are ignored, as are blank lines.

Parsing such a configuration file is now as simple as a single function
call:
```
    ...
    parseFileCL(&params, 'config-03.txt');
    ...
```
Note that both command line parameters and configuration files can be used
in the same program, and that their priority is simply determined by the
order of calling `parseCL` and `fileParseCL`.
