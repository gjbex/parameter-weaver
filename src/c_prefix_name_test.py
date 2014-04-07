#!/usr/bin/env python
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
'''Module to test the C implementation of command line argument
handling for the prefix name bug'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.templatefile import TemplateFile
from vsc.parameter_weaver.c.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.c.formatter import Formatter

from utils import parse_dump

class CRunTest(unittest.TestCase):
    '''Tests for the prefix parameter bug'''

    @classmethod
    def  setUpClass(self):
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main_dump.c', 'tmp/main_dump.c')
        file_name = 'tests/prefix_c.txt'
        parser = ParameterParser(Validator())
        parameters = parser.parse(file_name)
        formatter = Formatter(parameters)
        base_name = 'parser'
        TemplateFile.template_dir = 'tmpl'
        artifacts = formatter.get_artifacts(base_name)
        for artifact in artifacts:
            artifact.action(os.path.join('tmp', artifact.name))
        c_files = [x.name for x in artifacts if x.name.endswith('.c')]
        c_files.append('main_dump.c')
        self._exec_file = './cl_dump_test'
        args = ['gcc', '-o', self._exec_file] + c_files + ['-lm']
        os.chdir('tmp')
        exit_code = subprocess.call(args)
        if exit_code != 0:
            self.fail('link failed')

    @classmethod
    def tearDownClass(self):
        os.chdir('..')

    def test_default_run(self):
        result = subprocess.check_output([self._exec_file])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(0.0, float(values['Tmin']))
        self.assertAlmostEqual(1.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_T_option_run(self):
        result = subprocess.check_output([self._exec_file, '-T', '3.0'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(0.0, float(values['Tmin']))
        self.assertAlmostEqual(3.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_Tmin_option_run(self):
        result = subprocess.check_output([self._exec_file, '-Tmin', '3.0'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(3.0, float(values['Tmin']))
        self.assertAlmostEqual(1.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_Tmin_T_option_run(self):
        result = subprocess.check_output([self._exec_file, '-Tmin', '3.0', '-T', '4.0'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(3.0, float(values['Tmin']))
        self.assertAlmostEqual(4.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_T_Tmin_option_run(self):
        result = subprocess.check_output([self._exec_file, '-T', '4.0', '-Tmin', '3.0'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(3.0, float(values['Tmin']))
        self.assertAlmostEqual(4.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_Tmax_T_Tmin_option_run(self):
        result = subprocess.check_output([self._exec_file, '-Tmax', '-1.0', '-T', '4.0', '-Tmin', '3.0'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertAlmostEqual(3.0, float(values['Tmin']))
        self.assertAlmostEqual(4.0, float(values['T']))
        self.assertAlmostEqual(-1.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_Tm_option_run(self):
        result = subprocess.check_output([self._exec_file, '-Tm', '-1.0'])
        values = parse_dump(result)
        self.assertEqual(5, len(values))
        self.assertAlmostEqual(0.0, float(values['Tmin']))
        self.assertAlmostEqual(1.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])

    def test_Tminn_option_run(self):
        result = subprocess.check_output([self._exec_file, '-Tminn', '-1.0'])
        values = parse_dump(result)
        self.assertEqual(5, len(values))
        self.assertAlmostEqual(0.0, float(values['Tmin']))
        self.assertAlmostEqual(1.0, float(values['T']))
        self.assertAlmostEqual(2.0, float(values['Tmax']))
        self.assertEqual(self._exec_file, values['exec'])


if __name__ == '__main__':
    unittest.main()

