from logdog.core.roles.processor import BaseProcessor


class Stripper(BaseProcessor):
    def on_recv(self, data):
        data.message = data.message.strip()
        return self.output.send(data)