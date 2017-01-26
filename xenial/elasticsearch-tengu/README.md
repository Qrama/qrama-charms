# Overview
This subordinate charm pings the sojobo-api so that the sojobo-api can find
the location of every elasticsearch.

# Usage

This charm is a subordinate charm that can be deployed by using

The charm-name has to be of the following format: [controller-name]-[model-name]-est

    juju deploy ./xenial/elasticsearch-tengu <charm-name> --resource deb="./resources/elasticsearch-5.1.1.deb"
    juju add-relation elasticsearch-tengu:client metricbeat:elasticsearch
    juju deploy my-application
    juju add-relation my-application metrcibeat:beats-host


# Contact Information

- sebastien pattyn <sebastien.pattyn@qrama.io>
