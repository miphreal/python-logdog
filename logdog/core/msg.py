import json


class Msg(object):
    __slots__ = (
        'message',
        'source',
        'meta',
    )

    def __init__(self, message, source, meta=None):
        self.message = message
        self.source = source
        self.meta = meta

    def serialize(self):
        return {
            'msg': self.message,
            'src': self.source,
            'meta': self.meta,
        }

    def serialize_json(self):
        return json.dumps(self.serialize())

    @classmethod
    def deserialize_json(cls, data):
        d = json.loads(data)
        return cls(message=d.get('msg'),
                   source=d.get('src'),
                   meta=d.get('meta'))
