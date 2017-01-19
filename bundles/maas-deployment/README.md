## Overview
This bundle will deploy the maas-deployment bundle. This will deploy the sojobo-api together with the controller-MAAS subordinate charm.

###  Deployment

This bundle will currently be deployed as a local bundle.

`juju deploy ./path/to/maas-deployment-bundle`

The subordinate charm, controller-maas, will copy the required files in the right Sojobo-api directory on the machine and restart the Sojobo-api so that the specific API-calls for an MAAS-controller are available.  
