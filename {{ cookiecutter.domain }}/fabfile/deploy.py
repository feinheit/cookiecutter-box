from __future__ import print_function, unicode_literals

from fabric.api import execute, task
from fabric.colors import red
from fabric.utils import abort

from fabfile.config import local, cd, run


@task(default=True)
def deploy():
    execute('check')
    execute('deploy.styles')
    execute('deploy.code')


@task
def styles():
    local('cd %(box_sass)s && grunt build')
    for part in ['bower_components', 'css']:
        local(
            'rsync -avz %%(box_sass)s/%s'
            ' %%(box_server)s:%%(box_domain)s/%%(box_sass)s/' % part)
    with cd('%(box_domain)s'):
        run('venv/bin/python manage.py collectstatic --noinput')


@task
def code():
    with cd('%(box_domain)s'):
        result = run('git status --porcelain')
        if result:
            abort(red('Uncommitted changes detected, aborting deployment.'))

    execute('check')
    local('git push origin %(box_branch)s')
    with cd('%(box_domain)s'):
        run('git fetch')
        run('git reset --hard origin/%(box_branch)s')
        run('find . -name "*.pyc" -delete')
        run('venv/bin/pip install -r requirements/live.txt'
            ' --find-links file:///home/www-data/tmp/wheel/wheelhouse/')
        run('venv/bin/python manage.py migrate --noinput')
        run('venv/bin/python manage.py collectstatic --noinput')
        run('sctl restart %(box_domain)s:*')

    execute('versioning.fetch_live_remote')
