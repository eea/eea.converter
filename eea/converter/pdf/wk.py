""" wkhtmltopdf wrapper
"""
import os
import time
import errno
import shlex
import subprocess
import logging
import tempfile
from threading import Timer
from PyPDF2 import PdfFileMerger
from eea.converter import WK_COMMAND
from eea.converter.pdf import Html2Pdf
from eea.converter.job import _raiseTimeout, _output, _cleanup
from eea.converter.job import AsyncJob
logger = logging.getLogger('eea.converter')


class PdfJob(AsyncJob):
    """ OS job
    """
    def run(self, **kwargs):
        """ Run job
        """
        for dependency in self.dependencies:
            dependency.run(**kwargs)

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
                timer = Timer(self.timeout, _raiseTimeout,
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


class PdfMergeJob(PdfJob):
    """ Merge PDFs
    """
    def run(self, **kwargs):
        """ Run job
        """
        safe = kwargs.get('safe', True)
        errors = []
        out = PdfFileMerger()

        for dependency in self.dependencies:
            dependency.run(**kwargs)
            if dependency.path:
                with open(dependency.path, 'rb') as pdf:
                    try:
                        out.append(pdf)
                    except Exception, err:
                        errors.append(err)

        with open(self.path, 'wb') as pdf:
            out.write(pdf)

        if not os.path.getsize(self.path):
            self.cleanup()
            self.path = ''
            errors.append(
                IOError(errno.ENOENT, "Empty output PDF", self.path)
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
        if not pdfs:
            return default

        out = _output()

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(out)

        job = PdfMergeJob('', out, timeout, cleanup, dependencies=pdfs)
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

        out = _output()
        args.append(out)

        cleanup = set(kwargs.get('cleanup') or [])
        cleanup.add(out)

        job = PdfJob(args, out, timeout, cleanup)
        if dry_run:
            return job

        safe = kwargs.get('safe', True)
        job.run(safe=safe)
        return job

# BBB
Job = AsyncJob
__all__ = [
    AsyncJob.__name__,
    Job.__name__,
    WkHtml2Pdf.__name__,
]
