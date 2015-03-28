import os.path

from fabric.api import env, cd, prefix, run, get, local

env.user = 'ryankask'
env.virtualenv_name = 'esther'
env.code_dir = '~/src/esther'
env.db_backups_dir = '~/var/db-backups'
env.dev_db_name = 'esther'
env.hosts = ['ryankaskel.com']


def deploy(requirements='no', frontend='yes', restart='yes'):
    with cd(env.code_dir):
        run('git pull')

        if requirements == 'yes':
            with prefix(u'workon {}'.format(env.virtualenv_name)):
                run('pip install -r requirements/base.txt')

        if frontend == 'yes':
            run('npm install')
            run('bower install')
            run('gulp build')

    if restart == 'yes':
        run('~/webapps/esther/apache2/bin/restart')


def load_db():
    backups = run('ls -t1 {}'.format(env.db_backups_dir)).split()

    if not backups:
        print('No database dumps to download.')
        return

    get(os.path.join(env.db_backups_dir, backups[0]), '/tmp')
    local('dropdb {name}; createdb {name}'.format(name=env.dev_db_name))
    local_backup = os.path.join('/tmp', backups[0])
    local('gunzip -c {} | psql {}'.format(local_backup, env.dev_db_name))
    local('rm {}'.format(local_backup))
