from logdog.core.roles.processor import BaseProcessor


class Stripper(BaseProcessor):
    def on_recv(self, data):
        return self.output.send(data.strip())