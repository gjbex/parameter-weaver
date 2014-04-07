/*
 * ParameterWeaver: a code generator to handle command line parameters
 * and configuration files for C/C++/Fortran/R/Octave
 * Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cl_params.h"

int main(int argc, char *argv[]) {
    FILE *fp;
    int i;
    Params params;
    initCL(&params);
    if (argc > 1) {
        parseFileCL(&params, argv[1]);
    }
    if (strlen(params.out) > 0) {
        fp = fopen(params.out, "w");
    } else {
        fp = stdout;
    }
    if (params.verbose) {
        dumpCL(fp, "# ", &params);
    }
    for (i = 0; i < params.n; i++) {
        fprintf(fp, "%d\t%f\n", i, i*params.alpha);
    }
    if (fp != stdout) {
        fclose(fp);
    }
    finalizeCL(&params);
    return EXIT_SUCCESS;
}

