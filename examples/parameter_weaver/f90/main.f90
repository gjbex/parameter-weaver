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
program main
use cl_params
use iso_fortran_env
implicit none
type(params_type) :: params
integer :: unit_nr = 8, i, istat, next
call init_cl(params)
call parse_cl(params, next)
if (len(trim(params % out)) > 0) then
    open(unit=unit_nr, file=trim(params % out), action="write")
else
    unit_nr = output_unit
end if
if (params % verbose) then
    call dump_cl(unit_nr, "# ", params)
end if
do i = 1, params % n
    write (unit_nr, "(I3, F5.2)") i, i*params % alpha
end do
if (unit_nr /= output_unit) then
    close(unit=unit_nr)
end if
stop
end program main

