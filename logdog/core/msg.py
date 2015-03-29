import json
from tornado.escape import to_unicode
import umsgpack


class Msg(object):
    __slots__ = (
        'message',
        'source',
        'meta',
        'version',
    )

    def __init__(self, message, source, meta=None, version=1):
        self.message = to_unicode(message)
        self.source = to_unicode(source)
        self.meta = meta
        self.version = version

    def __str__(self):
        return self.message

    def update_message(self, message):
        self.message = to_unicode(message)

    def update_meta(self, d):
        if self.meta is None:
            self.meta = {}
        self.meta.update(d)

    def serialize(self):
        return {
            'msg': self.message,
            'src': self.source,
            'meta': self.meta,
            '_v': self.version,
        }

    @classmethod
    def deserialize(cls, data):
        return cls(message=data.get('msg'),
                   source=data.get('src'),
                   meta=data.get('meta'),
                   version=data.get('_v'))

    def serialize_json(self):
        return json.dumps(self.serialize())

    @classmethod
    def deserialize_json(cls, data):
        return cls.deserialize(json.loads(data))

    def serialize_jsonb(self):
        return umsgpack.dumps(self.serialize())

    @classmethod
    def deserialize_jsonb(cls, data):
        return cls.deserialize(umsgpack.loads(data))
