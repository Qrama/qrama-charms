# Overview
This subordinate charm pings the sojobo-api so that the sojobo-api can find
the location of every elasticsearch.

# Usage

This charm is a subordinate charm that can be deployed by using

    juju deploy elasticsearch-tengu
    juju add-relation elasticsearch-tengu:client metricbeat:elasticsearch
    juju deploy my-application
    juju add-relation my-application metrcibeat:beats-host


# Contact Information

- sebastien pattyn <sebastien.pattyn@qrama.io>
