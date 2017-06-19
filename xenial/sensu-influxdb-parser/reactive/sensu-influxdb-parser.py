import os
from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set, charm_dir, config, unit_private_ip, open_port
from charmhelpers.core.host import service_restart, chownr
from charmhelpers.core.templating import render
from charmhelpers.contrib.python.packages import pip_install


INSTALL_PATH = '/opt/sensu-influxdb-parser'


@when_not('parser.installed')
def install():
    for pkg in ['influxdb', 'python-crontab']:
        pip_install(pkg)
    if not os.path.isdir(INSTALL_PATH):
        os.mkdir(INSTALL_PATH)
    context = {'install_path': INSTALL_PATH}
    render('sensu-influxdb-parser.service', '/etc/systemd/system/sensu-influxdb-parser.service', context=context)
    status_set('blocked', 'Waiting for relation with InfluxDB')
    set_state('parser.installed')


@when('influxdb.available')
@when_not('parser.running')
def setup_tcpserver(influxdb):
    from influxdb import InfluxDBClient
    client = InfluxDBClient(influxdb.hostname(), influxdb.port(), influxdb.user(), influxdb.password())
    client.create_database('tengu_monitoring')
    context = {
        'host': unit_private_ip(),
        'influx_ip': influxdb.hostname(),
        'influx_port': influxdb.port(),
        'influx_user': influxdb.user(),
        'influx_pass': influxdb.password(),
        'influx_db': 'tengu_monitoring'
    }
    render('tcpserver.py', os.path.join(INSTALL_PATH, 'tcpserver.py'), context=context)
    service_restart('sensu-influxdb-parser')
    status_set('active', 'Parser running')
    set_state('parser.running')


@when('parser.running', 'endpoint.available')
def setup_endpoint(endpoint):
    open_port(9999)
    endpoint.configure(9999)
