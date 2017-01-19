## Overview
This bundle will deploy the Aws-deployment bundle. This will deploy the sojobo-api together with the controller-AWS subordinate charm.

###  Deployment

This bundle will currently be deployed as a local bundle.

`juju deploy ./path/to/aws-deployment-bundle`

The subordinate charm, controller-aws, will copy the required files in the right Sojobo-api directory on the machine and restart the Sojobo-api so that the specific API-calls for an AWS-controller are available. 
