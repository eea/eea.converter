""" Convert utilities
"""
import os
import tempfile
import logging
import sys
from subprocess import Popen, PIPE, STDOUT
from eea.converter import CAN_CONVERT_IMAGE, CAN_CONVERT_SVG

CLOSE_FDS = not sys.platform.startswith('win')

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

        Keyword arguments:
        path_from -- if given, ignore `data` param and use this file as input

        """
        if not self.can_convert:
            raise RuntimeError('ImageMagick is not installed. Aborting...')

        if not data_from.startswith('.'):
            data_from = '.%s' % data_from

        if not data_to.startswith('.'):
            data_to = '.%s' % data_to

        if kwargs.get('path_from'):
            tmp_from = kwargs['path_from']
        else:
            tmp_from = tempfile.mktemp(suffix=data_from)
            with open(tmp_from, 'wb') as from_file:
                from_file.write(data)
        tmp_to = tempfile.mktemp(suffix=data_to)


        width = kwargs.get('width', None)
        height = kwargs.get('height', None)
        resize = ''

        if data_from == '.svg' and CAN_CONVERT_SVG:
            if width and height:
                resize = '-w %s -h %s' % (width, height)
            cmd = "rsvg-convert %(input)s %(resize)s -f %(format)s -o %(output)s" % {
                'input': tmp_from,
                'output': tmp_to,
                'format': data_to.strip('.'),
                'resize': resize
            }
        else:
            if width and height:
                resize = '-resize %sx%s' % (width, height)
            cmd = "convert %(input)s %(resize)s %(output)s" % {
                'input': tmp_from,
                'output': tmp_to,
                'resize': resize
            }

        process = Popen(cmd, shell=True,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                        close_fds=CLOSE_FDS)
        res = process.stdout.read()
        if res:
            logger.debug(res)

        res = None
        # if multiple pages return first; better multipage support needed
        multiple_tmp_to = []
        if not os.path.exists(tmp_to):
            pattern_tmp_to = "%s-%%d.%s" % tuple(tmp_to.rsplit(".", 1))
            i = 0
            tmp_to = file_for_page = pattern_tmp_to % i
            while os.path.exists(file_for_page):
                multiple_tmp_to.append(file_for_page)
                i += 1
                file_for_page = pattern_tmp_to % i

        with open(tmp_to, 'rb') as to_file:
            res = to_file.read()

        if multiple_tmp_to:
            self.cleanup(*multiple_tmp_to)
        else:
            self.cleanup(tmp_to)
        if not kwargs.get('path_from'):
            self.cleanup(tmp_from)
        return res

    def __call__(self, data, **kwargs):
        """ execute the convertion
        """
        if getattr(data, 'read', None):
            data = data.read()
        res = None
        try:
            res = self.convert(data, **kwargs)
        except RuntimeError, err:
            logger.debug(err)
        except Exception, err:
            logger.warning(
                'Could not run converter with '
                'this arguments: %s'
                ' | Error: %s', kwargs, err)
        return res
