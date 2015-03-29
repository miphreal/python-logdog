from .base import BaseFormatter


class Formatter(BaseFormatter):
    defaults = BaseFormatter.defaults.copy_and_update(
        format=u'{msg.source!s}: {msg.message!s}',
        format_meta_name=None,  # None means 'replace msg.message'
    )

    def __init__(self, *args, **kwargs):
        super(Formatter, self).__init__(*args, **kwargs)
        self.format = self.config.format
        self.format_meta_name = self.config.format_meta_name

    def __str__(self):
        return u'FORMATTER'

    def on_recv(self, data):
        msg = self.format.format(msg=data)
        if self.format_meta_name is not None:
            data.update_meta({self.format_meta_name: msg})
        else:
            data.update_message(msg)
        return self.output.send(data)