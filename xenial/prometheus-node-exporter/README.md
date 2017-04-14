# Introduction
This is a subordinate charm, which install the [Prometheus node-exporter](https://github.com/prometheus/node_exporter) on all the machines of an application to collect machine info and sends it to a Prometheus server.

# Installation

```
juju deploy $JUJU_REPOSITORY/prometheus-node-exporter
juju add-relation prometheus-node-exporter [application-to-monitor]
juju add-relation prometheus-node-exporter prometheus:target
```

# Bugs
Report bugs on <a href="https://github.com/Qrama/prometheus-node-exporter-charm/issues">Github</a>

# Author
Mathijs Moerman <a href="mailto:mathijs.moerman@qrama.io">mathijs.moerman@qrama.io</a>
