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
[params, args] = parse_cl(params);
dump_cl(stdout, "", params);
if size(args, 1) > 0
    fprintf(stdout, "remainder = ");
    fprintf(stdout, "%s", args(1, :));
    for i = 2:size(args, 1)
        fprintf(stdout, ", %s", args(i, :));
    end
    fprintf(stdout, "\n");
end

