def get_unicode(text):
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding='utf-8', errors='ignore')