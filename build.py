
# Copyright (c) 2020 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pybuilder.core import use_plugin
from pybuilder.core import init
from pybuilder.core import Author
from pybuilder.core import task
from pybuilder.pluginhelper.external_command import ExternalCommandBuilder
from pybuilder.utils import read_file
import json

use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.coverage')
use_plugin('python.distutils')
use_plugin('filter_resources')

name = 'prunetags'
authors = [
    Author('Emilio Reyes', 'emilio.reyes@intel.com')
]
summary = 'A Python script that removes old pre-release tags from repos in a GitHub org'
url = 'https://github.com/edgexfoundry/cd-management/tree/prune-github-tags'
version = '0.0.2'
default_task = [
    'clean',
    'analyze',
    'cyclomatic_complexity',
    'package'
]


@init
def set_properties(project):
    project.set_property('unittest_module_glob', 'test_*.py')
    project.set_property('coverage_break_build', False)
    project.set_property('flake8_max_line_length', 120)
    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_scripts', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_ignore', 'E501, W503, F401, E722, W605')
    project.build_depends_on_requirements('requirements-build.txt')
    project.depends_on_requirements('requirements.txt')
    project.set_property('distutils_console_scripts',
        ['prune-github-tags = prunetags.cli:main'])


@task('cyclomatic_complexity', description='calculates and publishes cyclomatic complexity')
def cyclomatic_complexity(project, logger):
    try:
        command = ExternalCommandBuilder('radon', project)
        command.use_argument('cc')
        command.use_argument('-a')
        result = command.run_on_production_source_files(logger)
        if len(result.error_report_lines) > 0:
            logger.error('Errors while running radon, see {0}'.format(result.error_report_file))
        for line in result.report_lines[:-1]:
            logger.debug(line.strip())
        if not result.report_lines:
            return
        average_complexity_line = result.report_lines[-1].strip()
        logger.info(average_complexity_line)

    except Exception as exception:
        print('ERROR: unable to execute cyclomatic complexity due to: {}'.format(str(exception)))
