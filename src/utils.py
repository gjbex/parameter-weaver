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
import os

def determine_base_name(path):
    f_name = os.path.basename(path)
    (base_name, ext) = os.path.splitext(f_name)
    return base_name

import re

def parse_dump(text):
    values = {}
    for line in text.split('\n'):
        if len(line.strip()) > 0:
            parts = re.split(r'\s*=\s*', line, 2)
            if parts[0] == 'remainder':
                values[parts[0]] = list(parts[1].strip().split(','))
            else:
                values[parts[0]] = parts[1].strip()
    return values
    
