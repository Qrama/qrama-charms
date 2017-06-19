import socketserver
import json
import re
from influxdb import InfluxDBClient


def check_load(measurement):
    regex = r'CheckLoad .* load average \(1 CPU\): \[(.+?),.*\]'
    outputs = [{'name': 'used', 'unit': '%'}]
    for i, res in enumerate(re.search(regex, measurement.replace('\n', '')).groups()):
        outputs[i]['value'] = float(res)
    return outputs


def metrics_memory(measurement):
    regex = r'.*memory\.total ([0-9]*?) .*memory\.free ([0-9]*?) .*memory\.used ([0-9]*?) .*'
    outputs = [{'name': 'total', 'unit': 'kB'}, {'name': 'free', 'unit': 'kB'}, {'name': 'used', 'unit': 'kB'}]
    for i, res in enumerate(re.search(regex, measurement.replace('\n', '')).groups()):
        outputs[i]['value'] = int(res)
    return outputs


def metrics_disk_usage(measurement):
    regex = r'.*root\.used ([0-9]*?) .*root\.avail ([0-9]*?) .*root\.used_percentage ([0-9]*?) .*'
    outputs = [{'name': 'used', 'unit': 'MB'}, {'name': 'free', 'unit': 'MB'}, {'name': 'percentage_used', 'unit': '%'}]
    for i, res in enumerate(re.search(regex, measurement.replace('\n', '')).groups()):
        outputs[i]['value'] = int(res)
    return outputs


def mongodb_replica(measurement):
    if measurement == 'Check failed to run: not running with --replSet ()':
        return []
    else:
        measurement = measurement.replace('\n', '')
        outputs = [{'name': 'health', 'unit': None}, {'name': 'ping_to_master', 'unit': 'ms'}, {'name': 'delay_to_primary', 'unit': 's'}]
        ids = re.search(r'member_[0-9]+\.id ([0-9]+?) ', measurement).groups()
        names = re.search(r'member_[0-9]+\.name (.+?) ', measurement).groups()
        healths = re.search(r'member_[0-9]+\.health (.+?) ', measurement).groups()
        pings = re.search(r'member_[0-9]+\.pingMs (.+?) ', measurement).groups()
        delays = re.search(r'member_[0-9]+\.secondsBehindPrimary ([0-9]+?) ', measurement).groups()


MAPPING = {
    'check-load.rb': check_load,
    'metrics-memory.rb': metrics_memory,
    'metrics-disk-usage.rb': metrics_disk_usage
}


def prep_data(data):
    data = json.loads(data.decode('utf-8'))
    if 'subscribers' in data['check'].keys():
        controller, model, machine = data['client']['name'].split('/')
        subscribers = data['check']['subscribers']
        measurements = MAPPING[data['check']['command'].split('/')[-1]](data['check']['output'])
        for m in measurements:
            body = []
            for s in subscribers:
                body.append({
                    'measurement': data['check']['name'],
                    'time': data['check']['executed'],
                    'tags': {
                        'controller': controller,
                        'model': model,
                        'machine': machine,
                        'charm': data['check']['aggregate'],
                        'application': s.split('/')[0],
                        'unit': s.split('/')[1]
                    },
                    'fields': {'name': m['name'], 'value': m['value'], 'size': m['unit']}
                })
        return body


class MyTCPHandler(socketserver.StreamRequestHandler):
    influx = InfluxDBClient("{{influx_ip}}", {{influx_port}}, "{{influx_user}}", "{{influx_pass}}", "{{influx_db}}")

    def handle(self):
        self.data = self.rfile.readline().strip()
        self.data = prep_data(self.data)
        if self.data is not None:
            self.influx.write_points(self.data, time_precision='s')


if __name__ == "__main__":
    server = socketserver.TCPServer(("{{host}}", 9999), MyTCPHandler)
    server.serve_forever()
