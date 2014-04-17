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

from argparse import ArgumentParser, FileType
import importlib
import os
import sys

from vsc.parameter_weaver.params import WeaverError
from vsc.parameter_weaver.help_formatter import HelpFormatter

EXIT_SUCCESS = 0
UNIMPLEMENTED_LANG_ERROR = 2
PARAMETER_DEF_ERROR = 3
INVALID_TYPE_ERROR = 4
FORMAT_ERROR = 5

def main():
    langs = ['C', 'Fortran', 'R', 'octave']
    descr_str = ('Parameter Weaver generates code fragments in the '
                 'specified programming language to handle command '
                 'line parameters based on a definition file.')
    descr_str += ' Supported languages: {0}.'.format(', '.join(langs))
    copyleft = ('ParameterWeaver 2.0.2\n'
                'Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>;\n'
                'This program comes with ABSOLUTELY NO WARRANTY;\n'
                'This is free software, and you are welcome to redistribute it\n'
                'under certain conditions (GPL3).')
    epilog_str = copyleft
    arg_parser = ArgumentParser(description=descr_str,
                                epilog=epilog_str, prog='weave')
    format_group = arg_parser.add_mutually_exclusive_group()
    format_group.add_argument('--csv', action='store_true',
                              help='definition file is in CSV format')
    format_group.add_argument('--conf', action='store_true',
                              help='definition file is in config format')
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--definition', type=FileType('r'),
                       dest='file',
                       help='file containing parameter definitions')
    arg_parser.add_argument('--delimiter', dest='delimiter',
                            default=None, 
                            help='explicit delimiter for CSV definition file, skip autodection')
    arg_parser.add_argument('--application', dest='application',
                            default=None, help='application name')
    arg_parser.add_argument('--description', dest='description',
                            default=None,
                            help='application description string')
    arg_parser.add_argument('--copyright', dest='copyright',
                            default=None,
                            help='application copyright string')
    arg_parser.add_argument('--pre_params', dest='pre_params',
                            default='', help='parameters handled manually preceeding those handled by parameter weaver')
    arg_parser.add_argument('--post_params', dest='post_params',
                            default='', help='parameters handled manually following those handled by parameter weaver')
    arg_parser.add_argument('-l', '--lang', type=str, dest='language',
                            required=True,
                            help='target language to generate code in')
    arg_parser.add_argument('-b', '--base-name', type=str,
                            default='cl_params', dest='base_name',
                            help='base name for files containing '
                                 'generated code')
    arg_parser.add_argument('-t', '--type-name', type=str,
                            default=None, dest='type_name',
                            help='name for the type representing '
                                 'command line parameters')
    group.add_argument('-s', '--show-types', action='store_true',
                       dest='show_types',
                       help='print the supported bypes for the language '
                            'and exit')
    arg_parser.add_argument('-v', '--verbose', action='store_true',
                            dest='verbose',
                            help='print feedback to stderr, mainly for '
                                 'debugging')
    options = arg_parser.parse_args()
    lang = options.language.lower()
    tmpl_module = importlib.import_module('vsc.parameter_weaver.templatefile')
    params_module = importlib.import_module('vsc.parameter_weaver.params')
    base_validator = importlib.import_module('vsc.parameter_weaver.base_validator')
    try:
        validator_module = importlib.import_module('vsc.parameter_weaver.{0}.validator'.format(lang))
        formatter_module = importlib.import_module('vsc.parameter_weaver.{0}.formatter'.format(lang))
    except ImportError as error:
        sys.stderr.write('### error: language {0} is not implemneted\n'.format(options.language))
        sys.exit(UNIMPLEMENTED_LANG_ERROR)
    tmpl_module.TemplateFile.template_dir = os.environ['WEAVER_TMPL']
    validator = validator_module.Validator()
    if options.show_types:
        for lang_type in validator.types():
            print lang_type
        sys.exit(EXIT_SUCCESS)
    if options.conf:
        parser = params_module.ParameterConfigParser(validator)
    else:
        parser = params_module.ParameterCsvParser(validator,
                                                  options.delimiter)
    try:
        parameters = parser.parse_file(options.file)
    except base_validator.ParameterDefinitionError as error:
        sys.stderr.write('### error: {0}\n'.format(error))
        sys.exit(PARAMETER_DEF_ERROR)
    except WeaverError as error:
        sys.stderr.write('### error: {0}\n'.format(error))
        sys.exit(FORMAT_ERROR)
    help_formatter = HelpFormatter(parameters)
    help_formatter.application = options.application
    help_formatter.description = options.description
    help_formatter.copyright = options.copyright
    help_formatter.pre_params = options.pre_params
    help_formatter.post_params = options.post_params
    help_str = help_formatter.create_help()
    formatter = formatter_module.Formatter(parameters)
    formatter.help_str = help_str
    if options.type_name is not None:
        if validator.is_valid_type_name(options.type_name):
            formatter.struct_type_name = options.type_name
        else:
            sys.stderr.write("### error: '{0}' is not a valid type "
                             "name for {1}".format(options.type_name,
                                                   validator.programming_language))
            sys.exit(INVALID_TYPE_ERROR)
    artifacts = formatter.get_artifacts(options.base_name)
    for artifact in artifacts:
        if options.verbose:
            sys.stderr.write("### info: creating file '{0}'\n".format(artifact.name))
        artifact.action(artifact.name)
    
if __name__ == '__main__':
    main()

