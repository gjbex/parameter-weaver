* Code generation for usage information
  * implement Matlab version
  * implement Java version

* Add function to read default configuration file
  * order to try:
    * path in $<APPL>_CONFIG
    * ./<APPL>rc
    * ./.<APPL>rc
    * ~/.<APPL>rc
  * implementat C version
  * implementat Fortran version
  * implementat R version
  * implement Matlab version
  * implement Java version

* Add support for MPI
  MPI standard doesn't guarantee that each process can access command
  line arguments, hence add function to broadcast parameters
  * implementat C version
  * implementat Fortran version

* Add support for JSON parameter definition files

* Add support to specify that soe command line arguments are required

* Add automatic help generation (-h/--help)
