""" Watermark utility
"""

from PIL import Image, ImageEnhance

def reduce_opacity(im, opacity):
    """ Returns an image with reduced opacity
    """
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

class Watermark(object):
    """ Watermark utility
    """

    def placeWatermark(self, im, mark, position, opacity):
        """Adds a watermark to an image."""
        if opacity < 1:
            mark = reduce_opacity(mark, opacity)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')

        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        layer.paste(mark, position)
        return Image.composite(layer, im, layer)
