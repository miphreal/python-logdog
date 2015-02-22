import os


config = {
    'sources': [
        {'paths': [], 'tags': [],
         'pipe': 'file->webui'}

    ],

    # pipes log passing
    'pipes': {
        'file->webui': [
            {'watcher': 'default'},
            {'processor': ['strip']},
            {'forwarder': 'default'},
            {'tunnel': {'zqm-tunnel': {'in': {'connect': 'tcp://localhost:45457'},
                                       'out': {'bind': 'tcp://*:45457'}}}},
            {'viewer': {'webui': {}}},
        ]
    },

    # file listeners
    'watchers': {
        'default': {
            'cls': 'logdog.dog.watchers.FileWatcher',
            'poll_interval': 0.5,
            'max_poll_interval': 5 * 60,
            'poll_interval_count': 30,
            'buffer_size': 1024,
        },
    },

    # message processors/reducers/filters
    'processors': {
        'pass': None,
        'strip': '',
        'traceback': '',
        'parser': ''
    },

    # message forwarders
    'forwarders': {
        'pass': None,
        'default': {
            'cls': 'logdog.dog.forwarders.Forwarder',
            'consume_interval': 1.0,
        },
        'console': {}
    },

    # tunnels
    'tunnels': {
        'zmq-tunnel': {
            'cls': 'logdog.core.tunnels.ZMQTunnel',
            'in': {'socket': 'PUSH', 'connect': ['tcp://localhost:45457']},
            'out': {'socket': 'PULL', 'bind': ['tcp://localhost:45457']},
        }
    },

    # message viewers
    'viewers': {
        'webui': {
            'port': 8888,
            'address': '',
            'autoreload': False,
            'debug': False,
            'static_path': os.path.join(os.path.dirname(__file__), 'webui/static'),
            'template_path': os.path.join(os.path.dirname(__file__), 'webui/assets/html'),
        }
    }
}
