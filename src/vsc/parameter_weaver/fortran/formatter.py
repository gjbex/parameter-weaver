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
from vsc.parameter_weaver.fortran.types import CharacterArray, Logical
from vsc.util import Indenter

class Formatter(BaseFormatter):

    def __init__(self, parameters):
        super(Formatter, self).__init__(parameters)
        self.struct_type_name = 'params_type'
        self.indent_string = '    '
        self._def_ext = '.f90'

    def declaration(self):
        indenter = Indenter(self.indent_string)
        indenter.add('type :: {0}').incr()
        for param in self._parameters:
            indenter.add('{0} :: {1}'.format(param.type, param.name))
        indenter.decr().add('end type {0}')
        return indenter.text().format(self.struct_type_name)

    def initialization(self):
        indenter = Indenter(self.indent_string)
        indenter.add('subroutine init_cl(params)').incr()
        indenter.add('type(params_type), intent(out) :: params')
        for param in self._parameters:
            name = param.name
            default = param.default
            if isinstance(param.type, CharacterArray):
                indenter.add("params % {0} = '{1}'".format(name, default))
            elif isinstance(param.type, Logical):
                indenter.add('params % {0} = .false.'.format(name))
            else:
                indenter.add('params % {0} = {1}'.format(name, default))
        indenter.decr().add('end subroutine init_cl')
        return indenter.text()

    def parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('subroutine parse_cl(params, next)')
        indenter.incr()
        indenter.add('type(params_type), intent(inout) :: params')
        indenter.add('integer, intent(out), optional :: next')
        indenter.add('integer :: argc, i, last, status')
        indenter.add('character(len=1024) :: argv')
        indenter.add('last = 1')
        indenter.add('status = 0')
        indenter.add('do').incr()
        indenter.add('if (last <= command_argument_count()) then').incr()
        indenter.add('call get_command_argument(last, argv)')
        indenter.add('select case (argv)').incr()
        for param in self._parameters:
            name = param.name
            indenter.add("case ('-{0}')".format(name)).incr()
            if isinstance(param.type, Logical):
                indenter.add('params % {0} = .true.'.format(name))
            else:
                indenter.add('call shift_cl(last, argv)')
                indenter.add(param.type.input_conversion('params % {0}'.format(name)))
                indenter.add('if (status /= 0) then').incr()
                indenter.add("write (error_unit, '(A)') &")
                indenter.incr()
                indenter.add("'### error: invalid value for option ' // &")
                indenter.add("'''-{0}'' ' // &".format(name))
                indenter.add("'of type {0}'".format(param.type.name))
                indenter.add('stop')
                indenter.decr()
                indenter.decr().add('end if')
            indenter.decr()
        indenter.add('case default').incr()
        indenter.add('exit')
        indenter.decr()
        indenter.decr().add('end select')
        indenter.decr().add('else').incr()
        indenter.add('exit')
        indenter.decr().add('end if')
        indenter.add('last = last + 1')
        indenter.decr().add('end do')
        indenter.add('if (present(next)) then').incr()
        indenter.add('next = last')
        indenter.decr().add('end if')
        indenter.add('return')
        indenter.decr().add('end subroutine parse_cl')
        return indenter.text()

    def file_parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('subroutine parse_file_cl(params, file_name)').incr()
        indenter.add('type(params_type), intent(inout) :: params')
        indenter.add('character(len=1024), intent(in) :: file_name')
        indenter.add('integer :: status, file_unit = 8')
        indenter.add('character(len=1024) :: line_str, arg_name, sep, argv')
        indenter.add('status = 0')
        indenter.add("open(unit=file_unit, file=file_name, action='READ', iostat=status)")
        indenter.add('if (status /= 0) then').incr()
        indenter.add("write (error_unit, '(A)') &").incr()
        indenter.add("'### error: can not open file ' // file_name")
        indenter.decr()
        indenter.add('stop')
        indenter.decr().add('end if')
        indenter.add('do').incr()
        indenter.add("read(file_unit, '(A)', iostat=status) line_str")
        indenter.add('if (status /= 0) exit')
        indenter.add('if (len_trim(line_str) == 0) cycle')
        indenter.add("if (index(trim(line_str), '#') == 1) cycle")
        indenter.add('read (line_str, *, iostat=status) arg_name, sep, argv')
        indenter.add('if (status == 0) then').incr()
        indenter.add("if (sep /= '=') then").incr()
        indenter.add("write (error_unit, '(A)') &").incr()
        indenter.add("'### error, invalid line format: ' // line_str")
        indenter.decr()
        indenter.add('stop')
        indenter.decr().add('end if')
        indenter.add('select case (arg_name)').incr()
        for param in self._parameters:
            name = param.name
            indenter.add("case ('{0}')".format(name)).incr()
            indenter.add(param.type.input_conversion('params % {0}'.format(name)))
            indenter.add('if (status /= 0) then').incr()
            indenter.add("write (error_unit, '(A)') &")
            indenter.incr()
            indenter.add("'### error: invalid value for option ' // &")
            indenter.add("'''{0}'' ' // &".format(name))
            indenter.add("'of type {0}'".format(param.type.name))
            indenter.add('stop')
            indenter.decr()
            indenter.decr().add('end if')
            indenter.decr()
        indenter.add('case default').incr()
        indenter.add("write (error_unit, '(A)') &").incr()
        indenter.add("'### warning, unknown parameter ''' // &")
        indenter.add(" arg_name // ''' in line: ' // line_str")
        indenter.decr()
        indenter.decr()
        indenter.decr().add('end select')
        indenter.decr().add('else').incr()
        indenter.add("write (error_unit, '(A)') &").incr()
        indenter.add("'### error, invalid line format: ' // line_str")
        indenter.decr()
        indenter.add('stop')
        indenter.decr().add('end if')
        indenter.decr().add('end do')
        indenter.add('return')
        indenter.decr().add('end subroutine parse_file_cl')
        return indenter.text()

    def dumper(self):
        indenter = Indenter(self.indent_string)
        indenter.add('subroutine dump_cl(unit_nr, prefix, params)').incr()
        indenter.add('integer, intent(in) :: unit_nr')
        indenter.add('character(len=*), intent(in) :: prefix')
        indenter.add('type(params_type), intent(in) :: params')
        for param in self._parameters:
            name = param.name
            if isinstance(param.type, CharacterArray):
                indenter.add("write (unit_nr, '(A)') &")
                indenter.incr()
                indenter.add("prefix // &")
                indenter.add("'{0} = ''' // trim(params % {0}) // ''''".format(name))
            else:
                format = param.type.format_string
                indenter.add("write (unit_nr, '(A, {0})') &".format(format))
                indenter.incr()
                indenter.add("prefix // &")
                indenter.add("'{0} = ', params % {0}".format(name))
            indenter.decr()
        indenter.add('return')
        indenter.decr().add('end subroutine dump_cl')
        return indenter.text()

    def aux_functions(self):
        indenter = Indenter(self.indent_string)
        indenter.add('subroutine shift_cl(last, argv)').incr()
        indenter.add('integer, intent(inout) :: last')
        indenter.add('character(len=*), intent(inout) :: argv')
        indenter.add('if (last < command_argument_count()) then').incr()
        indenter.add('last = last + 1')
        indenter.add('call get_command_argument(last, argv)')
        indenter.decr().add('else').incr()
        indenter.add("write (error_unit, '(A)') &")
        indenter.incr()
        indenter.add("'### error: option ''' // trim(argv) // ''' expects a value'")
        indenter.decr()
        indenter.add('stop')
        indenter.decr().add('end if')
        indenter.add('return')
        indenter.decr().add('end subroutine shift_cl')
        indenter.add()
        indenter.add('subroutine trim_quotes_cl(str)').incr()
        indenter.add('character(len=*), intent(inout) :: str')
        indenter.add('integer :: i')
        indenter.add('do i = 2, len_trim(str)').incr()
        indenter.decr().add('end do')
        indenter.decr().add('end subroutine trim_quotes_cl')
        return indenter.text()

    def definition_file(self, file_name):
        indenter = Indenter(self.indent_string)
        indenter.add('module {0}'.format(file_name))
        indenter.add('use iso_fortran_env')
        indenter.add('implicit none')
        indenter.add()
        indenter.incr().add(self.declaration()).decr()
        indenter.add()
        indenter.add('contains').incr()
        indenter.add()
        indenter.add(self.aux_functions())
        indenter.add()
        indenter.add(self.initialization())
        indenter.add()
        indenter.add(self.parser())
        indenter.add()
        indenter.add(self.file_parser())
        indenter.add()
        indenter.add(self.dumper())
        indenter.add()
        indenter.decr().add('end module {0}'.format(file_name))
        return indenter.text()

    def get_artifacts(self, base_name):
        return [TemporaryFile(base_name, '.f90',
                self.definition_file(base_name))]
