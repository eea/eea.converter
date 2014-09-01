""" wkhtmltopdf wrapper
"""
import os
import shutil
import shlex
import subprocess
import logging
import tempfile
from threading import Timer
from eea.converter import WK_COMMAND, CAN_JOIN_PDFS
from eea.converter.pdf import Html2Pdf

logger = logging.getLogger('eea.converter')

def raiseTimeout(timeout, proc, args):
    """ Raise timeout error
    """
    logger.warn("Timeout error: timeout = %s; cmd = %s",
                     timeout, ' '.join(args))
    proc.kill()

def _cleanup(*files):
    """ Remove temporary files
    """
    for tmp in files:
        try:
            os.unlink(tmp)
        except Exception, err:
            logger.exception(err)

class Job(object):
    """ OS job
    """
    def __init__(self, cmd, output, timeout, cleanup, dependencies=None):
        if isinstance(cmd, (tuple, list)):
            self.cmd = ' '.join(cmd)
        else:
            self.cmd = cmd
        self.timeout = timeout
        self.toclean = set(cleanup)
        self.path = output
        self.dependencies = dependencies or []

    def cleanup(self):
        """ Remove temporary files
        """
        _cleanup(*self.toclean)

    def copy(self, src, dst):
        """
        :param src: Input file
        :param dst: Output file
        :return: status code, 0 for no errors
        """
        try:
            dirname = os.path.dirname(dst)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copyfile(src, dst)
        except Exception, err:
            logger.exception(err)
            return 1
        return 0

    def run(self, **kwargs):
        """ Run job
        """
        dependencies = []
        for dependency in self.dependencies:
            self.toclean.update(dependency.toclean)
            dependency.run(**kwargs)
            if dependency.path:
                dependencies.append(dependency.path)

        self.cmd = self.cmd % {
            'dependencies': ' '.join(dependencies)
        }

        args = shlex.split(self.cmd)

        try:
            proc = subprocess.Popen(
                args,
                stdin=tempfile.TemporaryFile(),
                stdout=tempfile.TemporaryFile(),
                stderr=tempfile.TemporaryFile()
            )

            if self.timeout:
                timer = Timer(self.timeout, raiseTimeout,
                              [self.timeout, proc, self.cmd])
                timer.start()
                proc.communicate()
                timer.cancel()
            else:
                proc.communicate()
        except Exception, err:
            logger.exception('%s. cmd: %s', err, self.cmd)
            self.cleanup()
            self.path = ''

        if self.path and not os.path.getsize(self.path):
            logger.warn('Empty output PDF. cmd = %s', self.cmd)
            self.cleanup()
            self.path = ''

class WkHtml2Pdf(Html2Pdf):
    """ Utility to convert html to pdf
    """
    def concat(self, pdfs, default=None, timeout=10, dry_run=False, **kwargs):
        """ Concat more PDF to one
        """
        if not CAN_JOIN_PDFS:
            return default

        if not pdfs:
            return default

        output = tempfile.mkstemp('.pdf')[1]
        cmd = ['pdftk', '%(dependencies)s', 'output', output]

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(output)

        job = Job(cmd, output, timeout, cleanup, dependencies=pdfs)
        if dry_run:
            return job

        job.run()
        return job

    def cleanup(self, *files):
        """ Remove tmp files
        """
        _cleanup(*files)

    def __call__(self, options, timeout=10, dry_run=False, **kwargs):

        args = [WK_COMMAND]
        args.extend(options)

        output = tempfile.mkstemp('.pdf')[1]
        args.append(output)

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(output)

        job = Job(args, output, timeout, cleanup)
        if dry_run:
            return job

        job.run()
        return job
