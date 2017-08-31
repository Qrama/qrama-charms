#!/usr/bin/env python3
from crontab import CronTab
import os
import random
from shutil import copyfile
from subprocess import check_output, CalledProcessError, STDOUT

from charmhelpers.core import unitdata
from charmhelpers.core.host import lsb_release, service_running, service_start, service_stop
from charmhelpers.core.hookenv import log, config, open_port, status_set, charm_dir
from charms.reactive import when, when_all, when_not, set_state, remove_state
from charms import layer, apt


db = unitdata.kv()


@when_not('apt.installed.letsencrypt')
def check_version_and_install():
    series = lsb_release()['DISTRIB_CODENAME']
    if not series >= 'xenial':
        log('letsencrypt not supported on series >= %s' % (series))
        status_set('blocked', "Unsupported series < Xenial")
        return
    else:
        apt.queue_install(['letsencrypt'])
        apt.install_queued()


@when('apt.installed.letsencrypt')
@when_not('letsencrypt.configured')
def initial_setup():
    db.set('fqdns', set())
    create_dhparam()
    open_port(80)
    open_port(443)
    set_state('letsencrypt.configured')


@when('letsencrypt.configured')
@when_not('lets-encrypt.registered', 'lets-encrypt.disable')
def register_server():
    fqdns = db.get('fqdns')
    if not fqdns:
        return
    # If the ports haven't been opened in a previous hook, they won't be open,
    # so opened_ports won't return them.
    ports = opened_ports()
    if not ('80/tcp' in ports or '443/tcp' in ports):
        status_set(
            'waiting',
            'Waiting for ports to open (will happen in next hook)')
        return
    needs_start = stop_running_web_service()
    mail_args = []
    if config().get('contact-email'):
        mail_args.append('--email')
        mail_args.append(config().get('contact-email'))
    else:
        mail_args.append('--register-unsafely-without-email')
    try:
        # Agreement already captured by terms, see metadata
        le_cmd = ['letsencrypt', 'certonly', '--standalone', '--agree-tos',
                  '--non-interactive']
        for fqdn in fqdns:
            le_cmd.extend(['-d', fqdn])
        le_cmd.extend(mail_args)
        output = check_output(
            le_cmd,
            universal_newlines=True,
            stderr=STDOUT)
        print(output)  # So output shows up in logs
        status_set('active', 'registered {}'.format(fqdns))
        set_state('lets-encrypt.registered')
    except CalledProcessError as err:
        status_set(
            'blocked',
            'letsencrypt registration failed: \n{}'.format(err.output))
        print(err.output)  # So output shows up in logs
    finally:
        if needs_start:
            start_web_service()
    unconfigure_periodic_renew()
    configure_periodic_renew()


@when_all('letsencrypt.configured', 'lets-encrypt.registered',
          # This state is set twice each day by crontab. This
          # handler will be run in the next update-status hook.
          'lets-encrypt.renew.requested')
@when_not('lets-encrypt.disable', 'lets-encrypt.renew.disable')
def renew_cert():
    remove_state('lets-encrypt.renew.requested')
    # We don't want to stop the webserver if no renew is needed.
    if no_renew_needed():
        return
    print("Renewing certificate...")
    configs = config()
    fqdns = configs.get('fqdns')
    needs_start = stop_running_web_service()
    try:
        output = check_output(
            ['letsencrypt', 'renew', '--agree-tos'],
            universal_newlines=True,
            stderr=STDOUT)
        print(output)  # So output shows up in logs
        status_set('active', 'registered {}'.format(str(fqdns)))
        set_state('lets-encrypt.renewed')
    except CalledProcessError as err:
        status_set(
            'blocked',
            'letsencrypt renewal failed: \n{}'.format(err.output))
        print(err.output)  # So output shows up in logs
    finally:
        if needs_start:
            start_web_service()


def no_renew_needed():
    # If renew is needed, the following call might fail because the needed
    # ports are in use. We catch this because we only need to know if a
    # renew was attempted, not if it succeeded.
    try:
        output = check_output(
            ['letsencrypt', 'renew', '--agree-tos'], universal_newlines=True)
    except CalledProcessError as error:
        output = error.output
    return "No renewals were attempted." in output


def stop_running_web_service():
    service_name = layer.options('lets-encrypt').get('service-name')
    if service_name and service_running(service_name):
        log('stopping running service: %s' % (service_name))
        service_stop(service_name)
        return True


def start_web_service():
    service_name = layer.options('lets-encrypt').get('service-name')
    if service_name:
        log('starting service: %s' % (service_name))
        service_start(service_name)


def configure_periodic_renew():
    command = (
        'export CHARM_DIR="{}"; '
        '/usr/local/bin/charms.reactive '
        'set_state lets-encrypt.renew.requested '
        ''.format(os.environ['CHARM_DIR']))
    cron = CronTab(user='root')
    jobRenew = cron.new(
        command=command,
        comment="Renew Let's Encrypt [managed by Juju]")
    # Twice a day, random minute per certbot instructions
    # https://certbot.eff.org/all-instructions/
    jobRenew.setall('{} 6,18 * * *'.format(random.randint(1, 59)))
    jobRenew.enable()
    cron.write()


def unconfigure_periodic_renew():
    cron = CronTab(user='root')
    jobs = cron.find_comment(comment="Renew Let's Encrypt [managed by Juju]")
    for job in jobs:
        cron.remove(job)
    cron.write()


def create_dhparam():
    copyfile(
        '{}/files/dhparam.pem'.format(charm_dir()),
        '/etc/letsencrypt/dhparam.pem')


def opened_ports():
    output = check_output(['opened-ports'], universal_newlines=True)
    return output.split()
