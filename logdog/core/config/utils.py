def handle_as_list(conf):
    if isinstance(conf, dict):
        return conf.items()
    if isinstance(conf, (list, tuple)):
        l = []
        for item in conf:
            if isinstance(item, basestring):
                l.append((item, None))
            elif isinstance(item, dict) and len(item) == 1:
                l.append(item.items()[0])
            elif isinstance(item, (list, tuple)) and item:
                l.append((item[0], item[1:] if len(item) > 2 else item[1]))
            else:
                l.append((item, None))
        return l
    return [(conf, None)]


def is_importable(key):
    return key in ('cls',)
