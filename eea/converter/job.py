""" Async job
"""
import os
import errno
import shutil
import logging
import tempfile
from zope.interface import implementer
from eea.converter.interfaces import IAsyncJob
from eea.converter.config import TMPDIR
logger = logging.getLogger('eea.converter')

#
# Abstract async job
#
@implementer(IAsyncJob)
class AsyncJob(object):
    """ Abstract async job
    """
    def __init__(self, cmd, output, timeout, cleanup, dependencies=None, **kw):
        if isinstance(cmd, (tuple, list)):
            self.cmd = ' '.join(cmd)
        else:
            self.cmd = cmd
        self.timeout = timeout
        self.toclean = set(cleanup)
        self.path = output
        self.dependencies = dependencies or []
        for key, value in kw.items():
            setattr(self, key, value)

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
        logger.warn('job.AsyncJob: Not implemented')


class TimeoutError(IOError):
    """ Timeout exception
    """


def _raiseTimeout(timeout, proc, cmd, errors):
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

def _output(prefix='eea.converter.', suffix='.pdf'):
    """ Provide an output tmp file
    """
    output = ''
    with tempfile.NamedTemporaryFile(
        prefix=prefix, suffix=suffix,
        dir=TMPDIR(), delete=False) as ofile:
        output = ofile.name
    return output
