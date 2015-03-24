#R documentation

##Data types

For R, ParameterWeaver supports the following data types:

  * `integer`
  * `double`
  * `logical`
  * `string`

##Example R script

Suppose we want to pass command line parameters to the following R script:
```
if (nchar(out) &gt; 0) {
    conn <- file(out, 'w')
} else {
    conn = stdout()
}
if (verbose) {
    write(sprintf("# n = %d\n", n), conn)
    write(sprintf("# alpha = %.16f\n", alpha), conn)
    write(sprintf("# out = '%s'\n", out), conn)
    write(sprintf("# verbose = %s\n", verbose), conn)
}
for (i in 1:n) {
    write(sprintf("%d\t%f\n", i, i*alpha), conn)
}
if (conn != stdout()) {
    close(conn)
}
```
We would like to set the number of iterations `n`, the factor `alpha`, the
name of the file to write the output to `out` and the verbosity `verbose`
at runtime, i.e., without modifying the source code of this script.

Moreover, the code to print the values of the variables is error prone, if
we later add or remove a parameter, this part of the code has to be updated
as well.

Defining the command line parameters in a parameter definition file to
automatlically generate the necessary code simplifies matters considerably.

##Example parameter definition file

The following file defines four command line parameters named `n`, `alpha`,
`out` and `verbose`.  They are to be interpreted as `integer`, `double`,
string and `logical` respectively, and if no values are passed via the
command line, they will have the default values `10`, `0.19`, `output.txt`
and false respectively.  Note that a string default value is quoted, just
as it would be in R code.  In this case, the columns in the file are
separated by tab characters.  The following is the contents of the
parameter definition file `param_defs.txt`:
```
integer	n	10
double	alpha	0.19
string	out	'output.txt'
logical	verbose	F
```
This parameter definition file can be created in a text editor such as the
one used to write R scripts, or from a Microsoft Excel worksheet by saving
the latter as a CSV file.

As mentioned above, logical values are also supported, however, the
semantics is slightly different from other data types.  The default value
of a logical variable is always false, regardless of what is specified in
the parameter definition file.  As opposed to parameters of other types, a
logical parameter acts like a flag, i.e., it is a command line options that
doesn't take a value.  Its absence is interpreted as false, its presence as
true.

##Generating code

Generating the code fragments is now very easy.  If appropriate, load the
module (thinking):
```
$ module load parameter-weaver
```
Next, we generate the code based on the parameter definition file:
```
$ weave -l R -d param_defs.txt
```

Three code fragments are generated, all grouped in a single R file
`cl_params.r`.

  * Initialization: the default values of the command line parameters are
    assigned to global variables with the names as specified in the
    parameter definition file.
  * Parsing: the options passed to the program via the command line are
    assigned to the appropriate variables.  Moreover, an array containing
    the remaining command line arguments is creaed as `cl_params`.
  * Dumper: a function is defined that takes two arguments: a file
    connector and a prefix.  This function writes the values of the command
    line parameters to the file connector, each on a separate line,
    preceeded by the specified prefix.

##Using the code fragments

The code fragments can be included into the R script by sourcing it:
```
  source("cl_parser.r")
```
The parameter initialization and parsing are executed at this point, the dumper can be called whenever the user likes, e.g.,
```
  dump_cl(stdout(), "")
```
The code for the script is thus modified as follows:
```
source('cl_params.r')
if (nchar(out) &gt; 0) {
    conn <- file(out, 'w')
} else {
    conn = stdout()
}
if (verbose) {
    dump_cl(conn, "# ")
}
for (i in 1:n) {
    cat(paste(i, "\t", i*alpha), file = conn, sep = "\n")
}
if (conn != stdout()) {
    close(conn)
}
```
Note that in this example, additional command line parameters are simply
ignored.  As mentioned before, they are available in the vector `cl_params`
if needed.
