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
import os.path
import shutil

from vsc.parameter_weaver.artifact import Artifact
from vsc.parameter_weaver.temporaryfile import TemporaryFile

class TemplateFile(TemporaryFile):

    template_dir = None

    def __init__(self, name, rel_path, vars={}):
        super(TemporaryFile, self).__init__(name)
        tmpl_path = os.path.join(TemplateFile.template_dir, rel_path)
        tmpl_file = open(tmpl_path)
        content = ''.join(tmpl_file.readlines()).format(**vars)
        self.write_tmp_file(content)

