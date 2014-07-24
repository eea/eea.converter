""" Utilities
"""
import urlparse

def truncate(text, length=300, orphans=10,
             suffix=u".", end=u".", cut=True, **kwargs):
    """
    Truncate text by the number of characters without cutting words at
    the end.

    >>> from eea.converter.utils import truncate
    >>> text = "This is a very long description. It needs to be truncated. "
    >>> text += "So what can we do?"


    Truncate by length:

    >>> truncate(text, length=60, orphans=3, suffix='..', end=None)
    u'This is a very long description. It needs to be truncated...'


    Truncate by sentences:

    >>> truncate(text, length=70, orphans=6, suffix='.', end='.')
    u'This is a very long description. It needs to be truncated.'

    >>> truncate(text, length=70, orphans=7, suffix='.', end='.')
    u'This is a very long description. It needs to be truncated. So what...do?'


    Avoid cutting at the end by using orphans:

    >>> truncate(text, length=70, orphans=7, suffix='..', end=None)
    u'This is a very long description. It needs to be truncated. So what...do?'

    Do not cut phrases.

    >>> truncate(text, length=10, orphans=5, suffix='.', cut=False)
    u''


    Keyword arguments:
    text -- text to truncate
    length -- maximum length of the output text
    orphans -- the number of trailing chars not to cut
    end -- sentence end char, usually "." If provided try to return only
    complete sentences

    """

    if isinstance(text, str):
        text = text.decode('utf-8')

    text = u' '.join(word for word in text.split() if word)
    if len(text) <= length + orphans:
        return text

    if end:
        res = []
        for chunk in text.split(end):
            if len(u".".join(res) + u'.' + chunk) <= (length + orphans):
                res.append(chunk)
                continue
            else:
                break

        if res:
            length = len(res)
            res = end.join(res)
            if res[-1] not in ['.', '!', '?'] and length > 1:
                res += suffix
            return res

    if cut:
        return u' '.join(text[:length+1].split()[:-1]) + suffix
    return u''

def absolute_url(context, url, default=None, **kwargs):
    """ Revert relative url to absolute url

    >>> from eea.converter.utils import absolute_url


    Won't touch absolute urls:

    >>> absolute_url(None, 'http://example.com/a/b/c')
    'http://example.com/a/b/c'

    >>> absolute_url(None, 'ftp://example.com/a/b/c')
    'ftp://example.com/a/b/c'


    Convert relative urls:

    >>> context = layer['portal']['sandbox']['doc']
    >>> absolute_url(context, url='../../sandbox-2?a=1&b=2')
    'http://nohost/plone/sandbox-2?a=1&b=2'


    Sometimes TinyMCE makes links relative to context's parent:

    >>> absolute_url(context, url='../sandbox-2?a=1&b=2')
    'http://nohost/plone/sandbox-2?a=1&b=2'


    If it can't resolve the url, you can specify a default fallback value:

    >>> absolute_url(context, url='../../sandbox-3', default='NotFound')
    'NotFound'


    Also, if the url contains a view (e.g. index.html, embed.png), specify it:

    >>> absolute_url(context, '../sandbox-2/embed.png?a=1', view='embed.png')
    'http://nohost/plone/sandbox-2/embed.png?a=1'


    Keyword arguments:
    context -- context on which url is relative
    url -- relative or absolute url
    default -- default if I can't find absolute url
    view -- Provide this if the url ends with a zope3 view (e.g. index.html,
    download.pdf)

    """
    if isinstance(url, unicode):
        url = url.encode('utf-8')

    if url.startswith('http'):
        return url

    if url.startswith('www.'):
        return 'http://%s' % url

    parsed = urlparse.urlparse(url)
    if parsed.scheme:
        return url

    query = ''
    if '?' in url:
        url, query = url.split('?')

    # Remove views from url
    view = kwargs.get('view', '')
    if view:
        url = url.replace('/%s' % view, '')

    # Relative url
    doc = context.restrictedTraverse(url, None)

    # Try parent
    if not doc:
        doc = context.getParentNode().restrictedTraverse(url, None)

    if not doc:
        return default

    url = doc.absolute_url()
    if view:
        url += '/' + view

    if query:
        url += '?' + query

    return url
