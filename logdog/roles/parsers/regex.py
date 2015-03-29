import re
from .base import BaseParser


class Regex(BaseParser):
    defaults = BaseParser.defaults.copy_and_update(
        regex=r'',
    )

    def __init__(self, *args, **kwargs):
        super(Regex, self).__init__(*args, **kwargs)
        self.re = re.compile(self.config.regex)

    def __str__(self):
        return u'REGEX-EXTRACTOR'

    def on_recv(self, data):
        match = self.re.search(data.message)
        if match:
            data.update_meta(match.groupdict())
        return self.output.send(data)