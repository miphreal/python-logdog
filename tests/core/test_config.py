# coding=utf-8
from hamcrest import *
import pytest

from logdog.core.config import ConfigLoader, Config, ConfigError


@pytest.fixture()
def config_path(tmpdir):
    p = tmpdir.join('config.yml')
    return p.strpath


@pytest.mark.userfixtures('config_path')
class TestConfigLoader(object):

    @pytest.fixture(autouse=True)
    def config_path_init(self, config_path):
        self.config_path = config_path

    def test_load_defaults(self):
        cl = ConfigLoader(path=None)
        conf = cl.load_config(default_only=True)

        assert_that(conf, all_of(
            # data is accessible both ways (attribute or key)
            has_key('sources'), has_property('sources'),
            has_key('pipes'), has_property('pipes'),
            has_key('options'), has_property('options'),
            has_key('pollers'), has_property('pollers'),
            has_key('collectors'), has_property('collectors'),
            has_key('processors'), has_property('processors'),
            has_key('formatters'), has_property('formatters'),
            has_key('forwarders'), has_property('forwarders'),
            has_key('connectors'), has_property('connectors'),
            has_key('viewers'), has_property('viewers'),
            has_key('utils'), has_property('utils'),
        ))

    def test_load_not_existing_file(self):
        cl = ConfigLoader(path=self.config_path)
        assert_that(
            calling(cl.load_config),
            raises(ConfigError, r'^\[.*\] Config file does not exist\.$'))

    def test_load_not_valid_file(self):
        with open(self.config_path, 'w') as f:
            f.write('')
        cl = ConfigLoader(path=self.config_path)
        assert_that(
            calling(cl.load_config),
            raises(ConfigError, r'^\[[^\]]*\] Invalid config file: must have "key: value" format\.$'))
