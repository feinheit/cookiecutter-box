from __future__ import unicode_literals

import os

from fabric.api import env, execute, require, task
from fabric.colors import red
from fabric.utils import abort

from fabfile import local, cd, run


@task(default=True)
def deploy():
    """Deploys frontend and backend code to the server if the checking step
    did not report any problems"""
    require('box_domain', provided_by='staging / production')

    execute('check')
    execute('deploy.styles')
    execute('deploy.code')


def _deploy_styles_foundation5_grunt():
    local('cd %(box_sass)s && grunt build')
    for part in ['bower_components', 'css']:
        local(
            'rsync -avz %%(box_sass)s/%s'
            ' %%(box_server)s:%%(box_domain)s/%%(box_sass)s/' % part)


def _deploy_styles_foundation4_bundler():
    local('bundle exec compass clean %(box_sass)s')
    local('bundle exec compass compile -s compressed %(box_sass)s')
    local(
        'rsync -avz %(box_sass)s/stylesheets'
        ' %(box_server)s:%(box_domain)s/%(box_sass)s/')


@task
def styles():
    """Compiles and compresses the CSS and deploys it to the server"""
    require('box_domain', provided_by='staging / production')

    if os.path.exists('%(box_sass)s/bower.json' % env):
        _deploy_styles_foundation5_grunt()
    elif os.path.exists('%(box_sass)s/config.rb' % env):
        _deploy_styles_foundation4_bundler()
    else:
        abort(red('I do not know how to deploy this frontend code.'))

    with cd('%(box_domain)s'):
        run('venv/bin/python manage.py collectstatic --noinput')


@task
def code():
    """Deploys the currently committed project state to the server, if there
    are no uncommitted changes on the server and the checking step did not
    report any problems"""
    require('box_domain', 'box_branch', provided_by='staging / production')

    execute('check.deploy')
    local('git push origin %(box_branch)s')
    with cd('%(box_domain)s'):
        run('git fetch')
        run('git reset --hard origin/%(box_branch)s')
        run('find . -name "*.pyc" -delete')
        run('venv/bin/pip install -r requirements/production.txt'
            ' --find-links file:///home/www-data/tmp/wheel/wheelhouse/')
        run('venv/bin/python manage.py migrate --noinput')
        run('venv/bin/python manage.py collectstatic --noinput')
        run('sctl restart %(box_domain)s:*')

    execute('versioning.fetch_remote')
