def make_cache_key(text):
    MEMCACHED_CONTROL_CHARS = [' ']
    for c in MEMCACHED_CONTROL_CHARS:
        text = text.replace(c,'')
    return text[:250]

