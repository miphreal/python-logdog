import os


config = {
    'watcher': {
        'default_cls': 'logdog.dog.watchers.FileWatcher',
        'targets': [
            {'paths': ['/var/log/syslog'], 'meta': {'type': 'syslog'}}
        ],
        'poll_interval': 0.5,
        'max_poll_interval': 5 * 60,
        'poll_interval_count': 30,
        'buffer_size': 1024,
    },
    'forwarder': {
        'default_cls': 'logdog.dog.forwarders.Forwarder',
        'consume_interval': 1.0,
        'upstream': ['tcp://localhost:45457'],
    },
    'webui': {
        'collector': ['tcp://*:45457'],
        'port': 8888,
        'address': '',
        'autoreload': False,
        'debug': False,
        'static_path': os.path.join(os.path.dirname(__file__), 'webui/static'),
        'template_path': os.path.join(os.path.dirname(__file__), 'webui/assets/html'),
    }
}
