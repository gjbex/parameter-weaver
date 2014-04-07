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
from vsc.parameter_weaver.octave.validator import String, Logical
from vsc.util import Indenter

class Formatter(BaseFormatter):

    def __init__(self, parameters):
        super(Formatter, self).__init__(parameters)
        self._def_ext = '.m'

    def initialization(self):
        indenter = Indenter(self.indent_string)
        indenter.add('function params = init_cl()').incr()
        for param in self._parameters:
            name = param.name
            default = param.default
            if isinstance(param.type, Logical):
                indenter.add('params.{0} = 0;'.format(name))
            elif isinstance(param.type, String):
                indenter.add("params.{0} = '{1}';".format(name, default))
            else:
                indenter.add('params.{0} = {1};'.format(name, default))
        indenter.decr().add('end')
        return indenter.text()

    def parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('function [new_params, args] = parse_cl(params)').incr()
        indenter.add('cl_params = argv();')
        indenter.add('cl_last = 1;')
        indenter.add('while cl_last <= size(cl_params, 1)').incr()
        indenter.add('switch char(cl_params(cl_last))').incr()
        for param in self._parameters:
            name = param.name
            indenter.add('case {{"-{0}"}}'.format(name)).incr()
            if isinstance(param.type, Logical):
                indenter.add('params.{0} = 1;'.format(name))
            else:
                indenter.add('cl_last = cl_last + 1;')
                indenter.add('if cl_last > size(cl_params, 1)').incr()
                indenter.add('fprintf(stderr, "### error: option \'-{0}\' expects a value");'.format(name))
                indenter.add('quit;')
                indenter.decr().add('end')
                indenter.add('argv_str = cl_params(cl_last);')
                val_func = param.type.validation_function('argv_str')
                indenter.add('if !{0}'.format(val_func)).incr()
                indenter.add('fprintf(stderr, "### error: invalid value for option \'-{0}\' of type {1}")'.format(name, param.type.name))
                indenter.add('quit;')
                indenter.decr().add('end')
                indenter.add(param.type.input_conversion('params.{0}'.format(name)))
            indenter.add('cl_last = cl_last + 1;')
            indenter.add('continue;')
            indenter.decr()
        indenter.add('endswitch')
        indenter.add('break;')
        indenter.decr().add('end')
        indenter.add('new_params = params;')
        indenter.add('if cl_last > size(cl_params, 1);').incr()
        indenter.add('args = [];')
        indenter.decr().add('else').incr()
        indenter.add('args = char(cl_params(cl_last:size(cl_params, 1)));')
        indenter.decr().add('end')
        indenter.decr().add('end')
        return indenter.text()

    def dumper(self):
        indenter = Indenter(self.indent_string)
        indenter.add('function dump_cl(fid, prefix, params)').incr()
        for param in self._parameters:
            name = param.name
            format_string = param.type.format_string
            if isinstance(param.type, String):
                indenter.add('fprintf(fid, "%s{0} = \'{1}\'\\n", prefix, params.{0});'.format(name, format_string))
            else:
                indenter.add('fprintf(fid, "%s{0} = {1}\\n", prefix, params.{0});'.format(name, format_string))
        indenter.decr().add('end')
        return indenter.text()

    def get_artifacts(self, base_name):
        return [
            TemporaryFile('init_cl', '.m', self.initialization()),
            TemporaryFile('parse_cl', '.m', self.parser()),
            TemporaryFile('dump_cl', '.m', self.dumper())]

