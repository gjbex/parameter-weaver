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
import shutil
import tempfile

from vsc.parameter_weaver.artifact import Artifact

class TemporaryFile(Artifact):

    def __init__(self, base_name, suffix, content):
        super(TemporaryFile, self).__init__(base_name + suffix)
        self.write_tmp_file(content)

    def write_tmp_file(self, content):
        (fd, self.path) = tempfile.mkstemp(text=True)
        artifact_file = os.fdopen(fd, 'w')
        artifact_file.write(content)
        artifact_file.close()

    def action(self, destination_path):
        shutil.copy(self.path, destination_path)

