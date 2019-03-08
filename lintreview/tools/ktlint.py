from __future__ import absolute_import
import logging
import os
import lintreview.docker as docker
from lintreview.tools import Tool, process_checkstyle

log = logging.getLogger(__name__)


class Ktlint(Tool):

    name = 'ktlint'

    def check_dependencies(self):
        """
        See if ktlint is on the system path.
        """
        return docker.image_exists('ktlint')

    def match_file(self, filename):
        """
        Check if a file should be linted using Ktlint.
        """
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext in ('.kt', '.kts')

    def process_files(self, files):
        """
        Run code checks with ktlint.
        """
        log.debug('Processing %s files with %s', files, self.name)
        
        command += files
        
        output = docker.run('ktlint', command, self.base_path)
        process_checkstyle(self.problems, output, docker.strip_base)

    def _create_command(self):
        command = ['ktlint', '--color', '--reporter=checkstyle']
        if self.options.get('android', False):
            command.append('--android')
        return command

    def has_fixer(self):
        """
        ktlin has a fixer that can be enabled through configuration.
        """
        return bool(self.options.get('fixer', False))

    def process_fixer(self, files):
        """Run ktlint in the fixer mode.
        """
        command = self.create_fixer_command(files)
        docker.run('ktlint', command, self.base_path)

    def create_fixer_command(self, files):
        command = self._create_command()
        command.append('--F')
        command += files
        return command