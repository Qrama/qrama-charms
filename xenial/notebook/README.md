# Overview

This subordinate charm needs to be deployed on the same machine as the Zeppelin charm.
```
juju deploy zeppelin
juju deploy zeppelin-notebook-deployer <notebook>
juju add-relation zeppelin <notebook>
```

# Configuration

#### notebook_location
- this the URL where the notebook can be found. The charm will then load the notebook in zeppelin.

# Contact Information
- Sébastien Pattyn <sebastien.pattyn@tengu.io>
