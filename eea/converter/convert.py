""" Convert utilities
"""
import os
import tempfile
import logging
from subprocess import Popen, PIPE, STDOUT
from eea.converter import CAN_CONVERT_IMAGE

logger = logging.getLogger('eea.converter')

class Convert(object):
    """ Convert images utility
    """

    def cleanup(self, *paths):
        """ Remove temporary files
        """
        for path in paths:
            try:
                os.unlink(path)
            except Exception, err:
                logger.warn(err)

    @property
    def can_convert(self):
        """ Are external tools installed
        """
        return CAN_CONVERT_IMAGE

    def convert(self, data, data_from=".pdf", data_to='.png', **kwargs):
        """ Converts raw data from given format to given format
        """
        if not self.can_convert:
            raise RuntimeError('ImageMagick is not installed. Aborting...')

        if not data_from.startswith('.'):
            data_from = '.%s' % data_from

        if not data_to.startswith('.'):
            data_to = '.%s' % data_to

        tmp_from = tempfile.mktemp(suffix=data_from)
        tmp_to = tempfile.mktemp(suffix=data_to)

        with open(tmp_from, 'wb') as from_file:
            from_file.write(data)

        width = kwargs.get('width', None)
        height = kwargs.get('height', None)
        resize = ''
        if width and height:
            resize = '-resize %sx%s' % (width, height)

        cmd = "convert %(input)s %(resize)s %(output)s" % {
            'input': tmp_from,
            'output': tmp_to,
            'resize': resize
        }

        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        res = None
        with open(tmp_to, 'rb') as to_file:
            res = to_file.read()

        self.cleanup(tmp_from, tmp_to)
        return res

    def __call__(self, data, **kwargs):
        if getattr(data, 'read', None):
            data = data.read()
        res = None
        try:
            res = self.convert(data, **kwargs)
        except RuntimeError, err:
            logger.debug(err)
        except Exception, err:
            logger.exception(
                'Could not run converter with '
                'this arguments: %s'
                'Error: %s', kwargs, err)
        return res
