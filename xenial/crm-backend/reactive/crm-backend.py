# pylint: disable=c0111,c0301
from hashlib import sha256
import os
import shutil
import subprocess
# Charm pip dependencies
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, log, config, open_port, close_port, unit_public_ip
from charmhelpers.core.host import service_restart, chownr, adduser
from charmhelpers.contrib.python.packages import pip_install

from charms.reactive import hook, when, when_not, set_state, remove_state


API_DIR = config()['api-dir']
USER = config()['api-user']
GROUP = config()['nginx-group']
HOST = config()['host'] if config()['host'] != '127.0.0.1' else unit_public_ip()
SETUP = config()['setup']
###############################################################################
# INSTALLATION AND UPGRADES
###############################################################################
@when_not('backend.installed')
def install():
    log('Installing CRM backend')
    install_api()
    set_state('backend.installed')


@hook('upgrade-charm')
def upgrade_charm():
    log('Updating CRM backend')
    install_api()
    set_state('backend.installed')


@when('backend.configured', 'nginx.passenger.available')
@when_not('backend.running')
def configure_webapp():
    if SETUP == 'client':
        close_port(80)
        close_port(443)
        render_httpsclient()
        open_port(443)
        open_port(80)
    elif SETUP == 'letsencrypt':
        close_port(80)
        close_port(443)
        render_httpsletsencrypt()
        open_port(80)
    else:
        close_port(80)
        close_port(443)
        render_http()
        open_port(80)
    restart_api()
    set_state('backend.running')
    status_set('active', 'The CRM backend is running!')


def install_api():
    # Install pip pkgs
    for pkg in ['Jinja2', 'Flask', 'pyyaml', 'click', 'pygments', 'apscheduler', 'Flask-PyMongo']:
        pip_install(pkg)
    mergecopytree('files/crm_backend', API_DIR)
    os.mkdir('{}/files'.format(API_DIR))
    adduser(USER)
    os.mkdir('/home/{}'.format(USER))
    chownr('/home/{}'.format(USER), USER, USER, chowntopdir=True)
    chownr(API_DIR, USER, GROUP, chowntopdir=True)


def render_httpsclient():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR, 'dhparam': config()['dhparam']}
    chownr(context['dhparam'], GROUP, 'root')
    if config()['fullchain'] == '' and config()['privatekey'] == '':
        chownr('/etc/letsencrypt/live/{}'.format(HOST), GROUP, 'root', chowntopdir=True)
        context['fullchain'] = '/etc/letsencrypt/live/{}/fullchain.pem'.format(HOST)
        context['privatekey'] = '/etc/letsencrypt/live/{}/privkey.pem'.format(HOST)
        render('crm-client.conf', '/etc/nginx/sites-enabled/crm-backend.conf', context)
    elif config()['fullchain'] != '' and config()['privatekey'] != '':
        context['fullchain'] = config()['fullchain']
        context['privatekey'] = config()['privatekey']
        render('crm-client.conf', '/etc/nginx/sites-enabled/crm-backend.conf', context)
    else:
        status_set('blocked', 'Invalid fullchain and privatekey config')


def render_httpsletsencrypt():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    if not os.path.isdir('{}/.well-known'.format(API_DIR)):
        os.mkdir('{}/.well-known'.format(API_DIR))
    chownr('{}/.well-known'.format(API_DIR), USER, GROUP, chowntopdir=True)
    render('crm-letsencrypt.conf', '/etc/nginx/sites-enabled/crm-backend.conf', context)


def render_http():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    render('crm-http.conf', '/etc/nginx/sites-enabled/crm-backend.conf', context)


def restart_api():
    service_restart('nginx')
    subprocess.check_call(['service', 'nginx', 'status'])


# Handeling changed configs
@when('backend.configured', 'config.changed')
def feature_flags_changed():
    configure_webapp()
    restart_api()


# Database setup
@when('mongodb.available')
@when_not('backend.running')
def setup_database(mongodb):
    render('settings.py', '{}/settings.py'.format(API_DIR), {'ip': HOST, 'api_key': sha256(os.urandom(256)).hexdigest(),
                                                             'api_dir': API_DIR,
                                                             'uri': list(mongodb.connection())[-1]['uri'],
                                                             'db': list(mongodb.connection())[-1]['db']})
    set_state('backend.configured')


@when('backend.installed', 'nginx.passenger.available')
@when_not('mongodb.available')
def waiting_for_relation():
    remove_state('backend.running')
    status_set('blocked', 'The CRM backend is installed. Waiting for relation with MongoDB!')
###############################################################################
# UTILS
###############################################################################
def mergecopytree(src, dst, symlinks=False, ignore=None):
    """"Recursive copy src to dst, mergecopy directory if dst exists.
    OVERWRITES EXISTING FILES!!"""
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        if symlinks and os.path.islink(src_item):
            if os.path.lexists(dst_item):
                os.remove(dst_item)
            os.symlink(os.readlink(src_item), dst_item)
        elif os.path.isdir(src_item):
            mergecopytree(src_item, dst_item, symlinks, ignore)
        else:
            shutil.copy2(src_item, dst_item)
