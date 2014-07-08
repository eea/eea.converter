""" wkhtmltopdf wrapper
"""
import os
import subprocess
import logging
import tempfile
from threading import Timer
from eea.converter import WK_COMMAND, CAN_JOIN_PDFS
from eea.converter.pdf import Html2Pdf

logger = logging.getLogger('eea.converter')

class WkHtml2Pdf(Html2Pdf):
    """ Utility to convert html to pdf
    """
    def concat(self, pdfs, default=None, timeout=10):
        """ Concat more PDF to one
        """
        if not CAN_JOIN_PDFS:
            return default

        if not pdfs:
            return default

        output = tempfile.mkstemp('.pdf')[1]
        pdfs.insert(0, 'pdftk')
        pdfs.extend([
            'output', output
        ])

        try:
            proc = subprocess.Popen(
                pdfs,
                stdin=tempfile.TemporaryFile(),
                stdout=tempfile.TemporaryFile(),
                stderr=tempfile.TemporaryFile()
            )

            if timeout:
                timer = Timer(timeout, proc.kill)
                timer.start()
                proc.communicate()
                timer.cancel()
            else:
                proc.communicate()

        except Exception, err:
            logger.exception(err)
            self.cleanup(output)
            return default
        else:
            return output

    def cleanup(self, *files):
        """
        :param files: Try to unlink given files
        :return: nothing
        """
        for tmp in files:
            try:
                os.unlink(tmp)
            except Exception, err:
                logger.exception(err)

    def __call__(self, options, timeout=10):

        args = [WK_COMMAND]
        args.extend(options)

        output = tempfile.mkstemp('.pdf')[1]
        args.append(output)

        # logger.info(args)

        try:
            proc = subprocess.Popen(
                args,
                stdin=tempfile.TemporaryFile(),
                stdout=tempfile.TemporaryFile(),
                stderr=tempfile.TemporaryFile()
            )

            if timeout:
                timer = Timer(timeout, proc.kill)
                timer.start()
                proc.communicate()
                timer.cancel()
            else:
                proc.communicate()

        except Exception, err:
            logger.exception(err)
            self.cleanup(output)
            return ''
        else:
            return output
