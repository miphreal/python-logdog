from logdog.core.roles.processor import BaseProcessor


class Stripper(BaseProcessor):

    def __str__(self):
        return u'STRIPPER'

    def on_recv(self, data):
        data.message = data.message.strip()
        return self.output.send(data)