from __future__ import unicode_literals

import re

from fabric.api import env


env.box_staging_enabled = False
env.box_project_name = '{{ cookiecutter.project_name }}'

env.box_environments = {
    'production': {
        'domain': '{{ cookiecutter.domain }}',
        'branch': 'master',
        'server': '{{ cookiecutter.server }}',
        'remote': 'production',
    },
    'staging': {
        'domain': 'stage.{{ cookiecutter.domain }}',
        'branch': 'master',
        'server': '{{ cookiecutter.server }}',
        'remote': 'staging',
    },
}

env.box_check = {
    'coding_style': [
        ('.', env.box_project_name),
        # ('venv/src/???', '???'),
    ],
    'exclude_from_jshint': (
        'ckeditor/|lightbox'
    ),
}


def derive_env_from_domain():
    env.update({
        'box_repository_name': re.sub(r'[^\w]+', '_', env.box_domain),
        'box_database_name': re.sub(r'[^\w]+', '_', env.box_domain),
        'box_sass': '%(box_project_name)s/static/%(box_project_name)s' % env,
        'box_server_name': env.box_server.split('@')[-1],
        'forward_agent': True,
        'hosts': [env.box_server],
    })
