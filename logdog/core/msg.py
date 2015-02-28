import json
import umsgpack


class Msg(object):
    version = 1
    __slots__ = (
        'message',
        'source',
        'meta',
        'version',
    )

    def __init__(self, message, source, meta=None, version=version):
        self.message = message
        self.source = source
        self.meta = meta
        self.version = version

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
