""" Utilities
"""

def truncate(text, length=300, orphans=10, suffix=u".", end=u"."):
    """
    Truncate text by the number of characters without cutting words at
    the end.

    Orphans is the number of trailing chars not to cut, for example

    If end char provided try to separate by it
    """

    if isinstance(text, str):
        text = text.decode('utf-8')

    text = u' '.join(word for word in text.split() if word)
    if len(text) <= length + orphans:
        return text

    if end:
        res = []
        for chunk in text.split(end):
            if len(u".".join(res) + chunk) <= length + orphans:
                res.append(chunk)
                continue
            elif res:
                return u".".join(res) + suffix

    return u' '.join(text[:length+1].split()[:-1]) + suffix
