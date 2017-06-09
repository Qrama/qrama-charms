import re


def parse(script, measurement):
    return MAPPING[script](measurement)


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


MAPPING = {
    'check-load.rb': check_load,
    'metrics-memory.rb': metrics_memory,
    'metrics-disk-usage.rb': metrics_disk_usage
}
