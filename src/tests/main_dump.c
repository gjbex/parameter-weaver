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
#include <assert.h>
#include <err.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "parser.h"

int main(int argc, char *argv[]) {
    int i;
    FILE *fp;
    Params params;
    initCL(&params);
    parseCL(&params, &argc, &argv);
    dumpCL(stdout, "", &params);
    if (argc > 1) {
        i = 1;
        printf("remainder = '%s'", argv[i]);
        for (i = 2; i < argc; i++) {
            printf(",'%s'", argv[i]);
        }
        printf("\n");
    }
    printf("exec = %s\n", argv[0]);
    finalizeCL(&params);
    return EXIT_SUCCESS;
}


