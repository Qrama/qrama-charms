import os
from charms.reactive import when, when_not, set_state
from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.templating import render
from charmhelpers.contrib.python.packages import pip_install


db = unitdata.kv()
INSTALL_PATH = '/opt/heartbeat'


@when('service.available')
@when_not('heartbeat.installed')
def install(service):
    for pkg in ['influxdb', 'python-crontab']:
        pip_install(pkg)
    if not os.path.isdir(INSTALL_PATH):
        os.mkdir(INSTALL_PATH)
    db.set('service_name', os.environ['JUJU_REMOTE_UNIT'].split('/')[0])
    status_set('blocked', 'Waiting for relation with InfluxDB')
    set_state('heartbeat.installed')


@when('influxdb.available', 'heartbeat.installed')
@when_not('heartbeat.configured')
def setup_cronjob(influxdb):
    from influxdb import InfluxDBClient
    from crontab import CronTab
    client = InfluxDBClient(influxdb.hostname(), influxdb.port(), influxdb.user(), influxdb.password())
    client.create_database('tengu_monitoring')
    context = {
        'influx_ip': influxdb.hostname(),
        'influx_port': influxdb.port(),
        'influx_user': influxdb.user(),
        'influx_pass': influxdb.password(),
        'influx_db': 'tengu_monitoring',
        'service_name': db.get('service_name')
    }
    render('heartbeat.py', os.path.join(INSTALL_PATH, '{}.py'.format(db.get('service_name'))), context=context)
    cron = CronTab(user='root')
    cron.remove_all()
    cron.write()
    job = cron.new(command='python3 {}'.format(os.path.join(INSTALL_PATH, '{}.py'.format(db.get('service_name')))))
    job.minute.every(1)
    cron.write_to_user(user='root')
    status_set('active', 'Heartbeat is running')
    set_state('heartbeat.configured')


@when('hearbeat.configured')
@when_not('service.available')
def stop_cron():
    from crontab import CronTab
    cron = CronTab(user='root')
    cron.remove_all()
    cron.write_to_user(user='root')
