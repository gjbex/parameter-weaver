#!/usr/bin/env Rscript
#
# ParameterWeaver: a code generator to handle command line parameters
# and configuration files for C/C++/Fortran/R/Octave
# Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

source('cl_params.r')
if (nchar(out) > 0) {
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

