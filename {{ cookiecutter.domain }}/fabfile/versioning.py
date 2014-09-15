from __future__ import unicode_literals

import getpass
import os

from fabric.api import env, hide, hosts, prompt, require, settings, task
from fabric.colors import red
from fabric.contrib.console import confirm
from fabric.utils import puts

from fabfile import local


@task
@hosts('')
def init_bitbucket():
    username = prompt('Username', default=os.environ.get('USER', ''))
    password = getpass.getpass('Password ')
    organization = prompt('Organization', default='feinheit')
    repository_name = prompt(
        'Repository',
        default=env.box_repository_name)

    if not confirm(
        'Initialize repository at https://bitbucket.org/%s/%s?' % (
            organization, repository_name)):

        puts(red('Bitbucket repository creation aborted.'))
        return 1

    if username and password and organization and repository_name:
        env.box_auth = '%s:%s' % (username, password)
        env.box_repo = '%s/%s' % (organization, repository_name)

        with hide('running'):
            local(
                'curl'
                ' -X POST -u %(box_auth)s -H "content-type: application/json"'
                ' https://api.bitbucket.org/2.0/repositories/%(box_repo)s'
                ' -d \'{"scm": "git", "is_private": true,'
                ' "forking_policy": "no_public_forks"}\'')

        with hide('everything'):
            with settings(warn_only=True):
                local('git remote rm origin')

        local('git remote add origin git@bitbucket.org:%(box_repo)s.git')
        local('git push -u origin master')


@task
@hosts('')
def add_remote():
    require('box_domain', provided_by='staging / production')

    with settings(warn_only=True):
        local(
            'git remote add -f %(box_remote)s %(box_server)s:%(box_domain)s/')


@task
@hosts('')
def fetch_remote():
    require('box_remote', provided_by='staging / production')

    with settings(warn_only=True):
        local('git fetch %(box_remote)s')
