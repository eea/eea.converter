""" Async jobs
"""
import os
import logging
import tempfile
from kv import KV
from zope import event
from eea.converter.interfaces import IContextWrapper
from eea.converter.config import TMPDIR
logger = logging.getLogger('eea.converter')


class AsyncInfo(object):
    """ Async Info """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
#
# Custom Exceptions
#
class ConversionError(IOError):
    """ Conversion error
    """

def run_async_job(context, job, success_event, fail_event, info=None, **kwargs):
    """ Async job
    """
    kwargs.update(getattr(info, '__dict__', {}))

    filepath = kwargs.get('filepath', '')
    filepath_lock = filepath + '.lock'
    filepath_meta = filepath + '.meta'

    url = kwargs.get('url', '')
    email = kwargs.get('email', '')
    etype = kwargs.get('etype', 'pdf')

    wrapper = IContextWrapper(context)(**kwargs)
    if not filepath:
        wrapper.error = 'Invalid filepath for output %s' % etype
        job.cleanup()

        event.notify(fail_event(wrapper))
        raise ConversionError(2, 'Invalid filepath for output %s' % etype, url)

    # Maybe another async worker is generating our file. If so, we update the
    # list of emails where to send a message when ready and free this worker.
    # The already running worker will do the job for us.
    if os.path.exists(filepath_lock) and os.path.exists(filepath_meta):
        update_emails(filepath_meta, email)
        job.cleanup()
        return

    # Maybe a previous async job already generated our file
    if file_exists(filepath):
        job.cleanup()
        event.notify(success_event(wrapper))
        return

    # Mark the begining of the convertion
    prefix = 'eea.%s.' % etype
    with tempfile.NamedTemporaryFile(
            prefix=prefix, suffix='.lock',
            dir=TMPDIR(), delete=False) as ofile:
        lock = ofile.name

    job.copy(lock, filepath_lock)
    job.toclean.add(filepath_lock)
    job.toclean.add(lock)

    # Share some metadata with other async workers
    with tempfile.NamedTemporaryFile(
            prefix=prefix, suffix='.meta',
            dir=TMPDIR(), delete=False) as ofile:
        meta = ofile.name

    job.copy(meta, filepath_meta)
    job.toclean.add(filepath_meta)
    job.toclean.add(meta)

    update_emails(filepath_meta, email)

    try:
        job.run(safe=False)
    except Exception, err:
        wrapper.error = err
        wrapper.email = get_emails(filepath_meta, email)
        job.cleanup()

        event.notify(fail_event(wrapper))
        errno = getattr(err, 'errno', 2)
        raise ConversionError(errno, err, url)

    if not job.path:
        wrapper.error = "Invalid output %s" % etype
        wrapper.email = get_emails(filepath_meta, email)
        job.cleanup()

        event.notify(fail_event(wrapper))
        raise ConversionError(2, 'Invalid output %s' % etype, url)

    wrapper.email = get_emails(filepath_meta, email)
    job.copy(job.path, filepath)
    job.cleanup()

    event.notify(success_event(wrapper))


def update_emails(filepath, email):
    """ Update metadata file with given email
    """
    email = email.strip()
    if not email:
        return

    try:
        db = KV(filepath, 'emails')
        db[email] = True
    except Exception, err:
        logger.exception(err)


def get_emails(filepath, default=''):
    """ Get emails from file comma separated if iterable is False
    """
    try:
        db = KV(filepath, 'emails')
        emails = db.keys()
    except Exception, err:
        logger.exception(err)
        return default
    return ','.join(emails)


def file_exists(path, touch=True):
    """ File exists on disk and it's not empty. If touch is True,
    it update file and parent directory modification time.
    """
    if not (os.path.exists(path) and os.path.getsize(path)):
        return False

    if touch:
        parent = os.path.dirname(path)
        try:
            os.utime(path, None)
            os.utime(parent, None)
        except Exception, err:
            logger.exception(err)

    return True
