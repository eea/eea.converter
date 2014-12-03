""" wkhtmltopdf wrapper
"""
import os
import time
import errno
import shutil
import shlex
import subprocess
import logging
import tempfile
from threading import Timer
from eea.converter import WK_COMMAND, CAN_JOIN_PDFS
from eea.converter.pdf import Html2Pdf
from eea.converter.config import TMPDIR

logger = logging.getLogger('eea.converter')

class TimeoutError(IOError):
    """ Timeout exception
    """

def raiseTimeout(timeout, proc, cmd, errors):
    """ Raise timeout error
    """
    proc.kill()

    errors.append(
        TimeoutError(errno.ETIME, "%ss timeout for cmd: %s" % (timeout, cmd))
    )

def _cleanup(*files):
    """ Remove temporary files
    """
    for tmp in files:
        try:
            os.unlink(tmp)
        except OSError, err:
            # Skip missing file
            if err.errno == errno.ENOENT:
                continue
            logger.exception(err)
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
        for dependency in self.dependencies:
            self.toclean.update(dependency.toclean)
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
            dependency.run(**kwargs)
            if dependency.path:
                dependencies.append(dependency.path)

        self.cmd = self.cmd % {
            'dependencies': ' '.join(dependencies)
        }

        args = shlex.split(self.cmd)
        safe = kwargs.get('safe', True)
        retry = kwargs.pop('retry', 0)

        errors = []

        try:
            proc = subprocess.Popen(
                args,
                stdin=tempfile.TemporaryFile(),
                stdout=tempfile.TemporaryFile(),
                stderr=tempfile.TemporaryFile()
            )

            if self.timeout:
                timer = Timer(self.timeout, raiseTimeout,
                              [self.timeout, proc, self.cmd, errors])
                timer.start()
                proc.communicate()
                timer.cancel()
            else:
                proc.communicate()
        except Exception, err:
            errors.append(err)

        if self.path and not os.path.getsize(self.path):

            #21149 Protect against random wkhtmltopdf Segmentation fault exit
            if retry < 3:
                retry += 1
                kwargs['retry'] = retry
                logger.warn('Retry %s cmd: %s', retry, self.cmd)
                time.sleep(retry)
                return self.run(**kwargs)

            self.cleanup()
            self.path = ''
            errors.append(
                IOError(errno.ENOENT, "Empty output PDF", self.cmd)
            )

        # Finish
        for error in errors:
            if not safe:
                raise error
            logger.exception(error)

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

        with tempfile.NamedTemporaryFile(
                prefix='eea.converter.', suffix='.pdf',
                dir=TMPDIR(), delete=False) as ofile:
            output = ofile.name

        cmd = ['pdftk', '%(dependencies)s', 'output', output]

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(output)

        job = Job(cmd, output, timeout, cleanup, dependencies=pdfs)
        if dry_run:
            return job

        safe = kwargs.get('safe', True)
        job.run(safe=safe)
        return job

    def cleanup(self, *files):
        """ Remove tmp files
        """
        _cleanup(*files)

    def __call__(self, options, timeout=10, dry_run=False, **kwargs):

        args = [WK_COMMAND]
        args.extend(options)

        with tempfile.NamedTemporaryFile(
                prefix='eea.converter.', suffix='.pdf',
                dir=TMPDIR(), delete=False) as ofile:
            output = ofile.name

        args.append(output)

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(output)

        job = Job(args, output, timeout, cleanup)
        if dry_run:
            return job

        safe = kwargs.get('safe', True)
        job.run(safe=safe)
        return job
