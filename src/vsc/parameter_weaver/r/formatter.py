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
from vsc.parameter_weaver.base_formatter import BaseFormatter
from vsc.parameter_weaver.temporaryfile import TemporaryFile
from vsc.parameter_weaver.r.validator import String, Logical
from vsc.util import Indenter

class Formatter(BaseFormatter):

    def __init__(self, parameters):
        super(Formatter, self).__init__(parameters)
        self._def_ext = '.r'

    def initialization(self):
        indenter = Indenter(self.indent_string)
        for param in self._parameters:
            name = param.name
            default = param.default
            if isinstance(param.type, Logical):
                indenter.add('{0} <- FALSE'.format(name))
            elif isinstance(param.type, String):
                indenter.add('{0} <- "{1}";'.format(name, default))
            else:
                indenter.add('{0} <- {1};'.format(name, default))
        return indenter.text()

    def parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('cl_params = commandArgs(trailingOnly = TRUE)')
        indenter.add('cl_last = 1')
        indenter.add('while (cl_last <= length(cl_params)) {')
        indenter.incr()
        for param in self._parameters:
            name = param.name
            indenter.add('if (cl_params[cl_last] == "-{0}") {{'.format(name))
            indenter.incr()
            if isinstance(param.type, Logical):
                indenter.add('{0} <- TRUE'.format(name))
            else:
                indenter.add('cl_last <- cl_last + 1')
                indenter.add('if (cl_last > length(cl_params)) {').incr()
                indenter.add('write("### error: option \'-{0}\' expects a value", stderr())'.format(name))
                indenter.add('quit()')
                indenter.decr().add('}')
                indenter.add('argv_str <- cl_params[cl_last]')
                val_func = param.type.validation_function('argv_str')
                indenter.add('if (!{0}) {{'.format(val_func)).incr()
                indenter.add('write("### error: invalid value for option \'-{0}\' of type {1}", stderr())'.format(name, param.type.name))
                indenter.add('quit()')
                indenter.decr().add('}')
                indenter.add(param.type.input_conversion(name))
            indenter.add('cl_last <- cl_last + 1')
            indenter.add('next')
            indenter.decr().add('}')
        indenter.add('break')
        indenter.decr().add('}')
        indenter.add('if (cl_last > length(cl_params)) {').incr()
        indenter.add('cl_params <- c()')
        indenter.decr().add('} else {').incr()
        indenter.add('cl_params <- cl_params[cl_last:length(cl_params)]')
        indenter.decr().add('}')
        return indenter.text()

    def dumper(self):
        indenter = Indenter(self.indent_string)
        indenter.add('dump_cl <- function(fileConn, prefix) {').incr()
        for param in self._parameters:
            name = param.name
            format_string = param.type.format_string
            if isinstance(param.type, String):
                indenter.add('write(sprintf("%s{0} = \'{1}\'", prefix, {0}), fileConn)'.format(name, format_string))
            else:
                indenter.add('write(sprintf("%s{0} = {1}", prefix, {0}), fileConn)'.format(name, format_string))
        indenter.decr().add('}')
        return indenter.text()

    def definition_file(self, file_name):
        '''Returns contents of definition file'''
        indenter = Indenter(self.indent_string)
        indenter.add(self.initialization())
        indenter.add()
        indenter.add(self.parser())
        indenter.add()
        indenter.add(self.dumper())
        return indenter.text()

    def get_artifacts(self, base_name):
        return [
            TemporaryFile(base_name, '.r', self.definition_file(base_name))]
