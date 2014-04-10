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
'''Module to test the C implementation'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterCsvParser, WeaverError
from vsc.parameter_weaver.templatefile import TemplateFile
from vsc.parameter_weaver.c.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.c.formatter import Formatter
from vsc.parameter_weaver.help_formatter import HelpFormatter

from utils import parse_dump

class CHelpRunTest(unittest.TestCase):
    '''Tests for the parameter definition formatter with help enabled'''

    @classmethod
    def  setUpClass(self):
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main_dump.c', 'tmp/main_dump.c')
        file_name = 'tests/descr_c.txt'
        parser = ParameterCsvParser(Validator())
        parameters = parser.parse(file_name)
        help_formatter = HelpFormatter(parameters)
        help_formatter.application = 'my_appl'
        help_formatter.description = 'brilliant application that predicts the future'
        help_formatter.copyright = '(c) 1999, Told You So.inc'
        formatter = Formatter(parameters)
        formatter.help_str = help_formatter.create_help()
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
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_first_option_run(self):
        result = subprocess.check_output([self._exec_file, '-a', '10'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'abcde'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_second_option_run(self):
        result = subprocess.check_output([self._exec_file, '-f', '3.14'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_first_second_option_run(self):
        result = subprocess.check_output([self._exec_file, '-f', '3.14', '-a', '10'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(3.14, float(values['f']))
        self.assertEqual("'abcde'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_first_third_option_run(self):
        result = subprocess.check_output([self._exec_file, '-my_string', 'alpha', '-a', '10'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'alpha'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_all_options_run(self):
        result = subprocess.check_output([self._exec_file, '-my_string', 'alpha', '-a', '10', '-f', '-3.14'])
        values = parse_dump(result)
        self.assertEqual(4, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(-3.14, float(values['f']))
        self.assertEqual("'alpha'", values['my_string'])
        self.assertEqual(self._exec_file, values['exec'])

    def test_first_no_value(self):
        result = subprocess.check_output('{0} -a; exit 0'.format(self._exec_file),
                                         stderr=subprocess.STDOUT, shell=True)
        self.assertEqual("### error: option '-a' expects a value\n", result)

    def test_first_third_option_one_additional_run(self):
        result = subprocess.check_output([self._exec_file, '-my_string', 'alpha', '-a', '10', 'abc'])
        values = parse_dump(result)
        self.assertEqual(5, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'alpha'", values['my_string'])
        self.assertEqual(1, len(values['remainder']))
        self.assertEqual(1, len(values['remainder']))
        self.assertEqual("'abc'", values['remainder'][0])
        self.assertEqual(self._exec_file, values['exec'])

    def test_first_third_option_two_additional_run(self):
        result = subprocess.check_output([self._exec_file, '-my_string', 'alpha', '-a', '10', 'abc', 'cde ghi'])
        values = parse_dump(result)
        self.assertEqual(5, len(values))
        self.assertEqual(10, int(values['a']))
        self.assertAlmostEqual(0.19, float(values['f']))
        self.assertEqual("'alpha'", values['my_string'])
        self.assertEqual(2, len(values['remainder']))
        self.assertEqual("'abc'", values['remainder'][0])
        self.assertEqual("'cde ghi'", values['remainder'][1])
        self.assertEqual(self._exec_file, values['exec'])

    def test_help(self):
        result = subprocess.check_output([self._exec_file, '-my_string', 'alpha', '-?'], stderr=subprocess.STDOUT)
        target_lines = []
        with open('../tests/descr_help.txt', 'r') as help_file:
            for line in help_file:
                target_lines.append(line.rstrip('\n\r'))
        target = '\n'.join(target_lines)
        self.assertEqual(target, result)


if __name__ == '__main__':
    unittest.main()

