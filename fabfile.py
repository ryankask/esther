from fabric.api import *

env.user = 'ryankask'
env.virtualenv_name = 'esther'
env.code_dir = '~/src/esther'

@hosts(['ryankaskel.com'])
def deploy(requirements='no', restart='yes'):
    with cd(env.code_dir):
        run('git pull')

        if requirements == 'yes':
            with prefix(u'workon {0}'.format(env.virtualenv_name)):
                run('pip install -r requirements/base.txt')

    if restart == 'yes':
        run('~/webapps/esther/apache2/bin/restart')
