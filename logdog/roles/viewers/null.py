from .base import BaseViewer


class Null(BaseViewer):
    def _input_forwarder(self, data):
        pass

    on_recv = _input_forwarder