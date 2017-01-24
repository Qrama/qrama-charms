## Overview
This bundle will deploy the model-monitor-bundle that needs to be deployed is a model needs monitoring. This will deploy the Elasticsearch-tengu charm and the trusty and xenial tengubeat and add a relation with the EST and the beats.

###  Deployment

This bundle will currently be deployed as a local bundle.

`juju deploy ./path/to/model-monitor-bundle`

The subordinate charm, tengubeat, will retrieve information from the machine he is attached to and Elasticsearch-Tengu will gather all these information. The Sojobo is then able to get that information. The name of th eElasticsearch-tengu may not be changed!! The service name gets rendered when the bundle needs to be deployed.
