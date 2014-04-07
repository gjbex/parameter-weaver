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
params = init_cl();
params = parse_cl(params);
if (size(params.out) > 0)
    fid = fopen(params.out, "w");
else
    fid = stdout;
end
if (params.verbose)
    dump_cl(stdout, "# ", params);
end
for i = 1:params.n
    fprintf(fid, "%d\t%f\n", i, i*params.alpha);
end
if (fid != stdout)
    fclose(fid);
end

