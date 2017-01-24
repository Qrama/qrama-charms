﻿## Overview
This bundle will deploy the google-deployment bundle. This will deploy the sojobo-api together with the controller-GOOGLE subordinate charm.

###  Deployment

This bundle will currently be deployed as a local bundle.

`juju deploy ./path/to/google-deployment-bundle`

The subordinate charm, controller-google, will copy the required files in the right Sojobo-api directory on the machine and restart the Sojobo-api so that the specific API-calls for an GOOGLE-controller are available.  