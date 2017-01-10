# Overview

Metricbeat is a lightweight Shipper for Metrics. It Collects metrics from your
systems and services. From CPU to memory, Redis to Nginx, and much more...

# Usage

Metricbeat can be added to any principal charm thanks to the wonders of being
a subordinate charm. The following example will deploy the metricbeat on top
of the beats core bundle.
```
juju deploy elasticsearch
juju deploy my-service
juju deploy metricbeat
juju add-relation metricbeat:beats-host my-service
juju add-relation metricbeat elasticsearch
```
# Contact Information

- sebastien pattyn <sebastien.pattyn@qrama.io>
