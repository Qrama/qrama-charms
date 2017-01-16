# qrama-charms
This repository contains the all the qrama charms

## how to deploy 
- make sure you clone this repo
    git clone https://github.com/Qrama/qrama-charms.git
    
#### Sojobo-api

    juju deploy path/to/charm <charm name>

deploy the other necessary subordinatecharms:

    juju deploy path/to/charm monitor-api
    juju add-relation monitor-api <charm-name>

##### Elasticsearch-Tengu
 in `config.yaml`:
 - change api-key and sojobo-ip options to the right values

deployment:

    cd qrama-charms
    juju deploy ./xenial/elasticsearch-tengu aws-default-est --resource deb="./resources/elasticsearch-5.1.1.deb"
