!
! ParameterWeaver: a code generator to handle command line parameters
! and configuration files for C/C++/Fortran/R/Octave
! Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
! 
! This program is free software: you can redistribute it and/or modify
! it under the terms of the GNU General Public License as published by
! the Free Software Foundation, either version 3 of the License, or
! any later version.
! 
! This program is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
! 
! You should have received a copy of the GNU General Public License
! along with this program.  If not, see <http://www.gnu.org/licenses/>.
!
program params_dumper
use parser
use iso_fortran_env
implicit none
type(params_type) :: params
character(len=1024) :: file_name
integer :: istat
call init_cl(params)
if (command_argument_count() > 0) then
    call get_command_argument(1, file_name)
    call parse_file_cl(params, file_name)
end if
call dump_cl(output_unit, '', params)
end program params_dumper

