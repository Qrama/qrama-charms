import socketserver
import json
from influxdb import InfluxDBClient
from filters import *


MAPPING = {
    'check-load.rb': machine.check_load,
    'metrics-memory.rb': machine.metrics_memory,
    'metrics-disk-usage.rb': machine.metrics_disk_usage,
    'metrics-mongodb-replication.rb': mongodb.metrics_replica,
    'metrics-mongodb.rb': mongodb.metrics,
}


def prep_data(data):
    data = json.loads(data.decode('utf-8'))
    if 'subscribers' in data['check'].keys():
        controller, model, machine = data['client']['name'].split('-X-')
        subscribers = data['check']['subscribers']
        parser = MAPPING[data['check']['command'].split('/')[-1]]
        measurements = parser(data['check']['output'])
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
