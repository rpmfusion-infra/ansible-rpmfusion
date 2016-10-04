config = {
    'logging': {
        'loggers': {
            'robosignatory': {
                'handlers': ['console', 'mailer'],
                'level': 'DEBUG',
                'propagate': False
            },
        },
    },

    'robosignatory.enabled.tagsigner': True,
    'robosignatory.signing.user': 'autopen',
    'robosignatory.signing.passphrase_file': '/etc/sigul/autosign.pass',
    'robosignatory.signing.config_file': '/etc/sigul/client.conf',

    # The keys here need to be the same in the sigul bridge
    'robosignatory.koji_instances': {
        'primary': {
            'url': 'https://koji.rpmfusion.org/kojihub',
            'options': {
                # Only ssl is supported at the moment
                'authmethod': 'ssl',
                'cert': '/etc/sigul/autopen.pem',
                'serverca': '/etc/sigul/fedoraca.pem',
            },
            'tags': [
                {
                    "from": "f23-free-candidate",
                    "key": "f23-free",
                    "keyid": "e051b67e",
                    "to": "f23-free-updates-testing"
                },
                {
                    "from": "f24-free-candidate",
                    "key": "f24-free",
                    "keyid": "b7546f06",
                    "to": "f24-free-updates-testing"
                },
                {
                    "from": "f25-free-candidate",
                    "key": "f25-free",
                    "keyid": "6806a9cb",
                    "to": "f25-free-updates-testing"
                },
                {
                    "from": "f23-nonfree-candidate",
                    "key": "f23-nonfree",
                    "keyid": "e051b67e",
                    "to": "f23-nonfree-updates-testing"
                },
                {
                    "from": "f24-nonfree-candidate",
                    "key": "f24-nonfree",
                    "keyid": "b7546f06",
                    "to": "f24-nonfree-updates-testing"
                },
                {
                    "from": "f25-nonfree-candidate",
                    "key": "f25-nonfree",
                    "keyid": "6806a9cb",
                    "to": "f25-nonfree-updates-testing"
                }

            ]
        },
    },
}
