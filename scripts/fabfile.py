# -*- coding: utf-8 -*-
from fabric.api import run, cd, env
from fabric.utils import puts

env.use_ssh_config = True

APP_NAME = 'taboo'


def update():
    with cd("~/{}".format(APP_NAME)):
        puts("updating {}...".format(APP_NAME))
        run('git pull')
    puts('restarting server...')
    run("supervisorctl restart {}".format(APP_NAME))
