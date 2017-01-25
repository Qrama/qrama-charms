# qrama-charms
This repository contains the all the qrama charms

## how to deploy 
- make sure you clone this repo:
```shell
git clone https://github.com/Qrama/qrama-charms.git
```

#### Sojobo-api

    juju deploy path/to/charm <charm name>

deploy the other necessary subordinatecharms:

    juju deploy path/to/charm monitor-api
    juju add-relation monitor-api <charm-name>

#### Elasticsearch-Tengu
 in `config.yaml`:
 - change api-key and sojobo-ip options to the right values

deployment:

    cd qrama-charms
    juju deploy ./xenial/elasticsearch-tengu <charm-name> --resource deb="./resources/elasticsearch-5.1.1.deb"
    juju expose <charm-name> 
    
The charm-name has to be of the following format: [controller-name]-[model-name]-est

#### Metricbeats
Trusty:

    cd qrama-charms
    juju deploy ./trusty/metricbeat trustybeat
    juju deploy cs:trusty/application
    juju add-relation applications trustybeat:beats-host
    juju add-relation trustybeat:elasticsearch aws-default-est:client

Xenial:

    cd qrama-charms
    juju deploy ./xenial/metricbeat xenialbeat
    juju deploy cs:xenial/application
    juju add-relation applications xenialbeat:beats-host
    juju add-relation xenialbeat:elasticsearch aws-default-est:client
    
