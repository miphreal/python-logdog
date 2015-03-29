from .base import BaseProcessor


class Stripper(BaseProcessor):

    def __str__(self):
        return u'STRIPPER'

    def on_recv(self, data):
        data.update_message(data.message.strip())
        return self.output.send(data)