import os
from subprocess import check_call, CalledProcessError
from time import sleep
from influxdb import InfluxDBClient


def check_status():
    with open(os.devnull, 'wb') as hide_output:
        try:
            check_call(['/bin/systemctl', 'status', '{{service_name}}'], stdout=hide_output, stderr=hide_output)
            res = {'status': 'RUNNING'}
        except CalledProcessError:
            res = {'status': 'DOWN'}
    return res


if __name__ == "__main__":
    client = InfluxDBClient("{{influx_ip}}", {{influx_port}}, "{{influx_user}}", "{{influx_pass}}", "{{influx_db}}")
    res = {
        'measurement': 'heartbeat',
        'tags': {'name': '{{service_name}}'},
    }
    for i in range(0,11):
        res['fields'] = check_status()
        client.write_points([res])
        sleep(5)
