# Info
This is a subordinate charm for the Sojobo-api.

# Installation
This installation assumes a running version of the Sojobo-API. If this is not the case, one must be setup first, using the instructions provided here.

The required charms can be found in the qrama-charms repo. In order to install these using the following commands, one must be in the topdir of the cloned qrama-charms repo.
```
juju deploy cs:rabbitmq-server-61
juju deploy cs:~chris.macnaughton/influxdb-7
juju deploy ./xenial/monitoring-api
juju deploy ./xenial/sensu-base
juju deploy ./yakkety/redis
juju expose rabbitmq-server
```
Sensu provides it's own tool to generate all the required SSL-certificates, which are valid for 5 years. More info can be found here https://sensuapp.org/docs/latest/reference/ssl.html. Short version:
```
wget http://sensuapp.org/docs/0.29/files/sensu_ssl_tool.tar
tar -xvf sensu_ssl_tool.tar
cd sensu_ssl_tool
./ssl_certs.sh generate
```
Executing the following commands will parse all the correct ssl settings to the applications. It assumes you are in the sensu_ssl_tool dir.
```
juju config rabbitmq-server ssl_key="`cat server/key.pem`" ssl_cert="`cat server/cert.pem`" ssl_ca="`cat sensu_ca/cacert.pem`" ssl_enabled=True

juju config sensu-base ssl_key="`cat client/key.pem`" ssl_cert="`cat client/cert.pem`"

juju config monitoring-api ssl_key="`cat client/key.pem`" ssl_cert="`cat client/cert.pem`"
juju config monitoring-api rabbitmq="[publicip:port rabbitmq server. Port is ssl port, default 5671]"
```
Then some of the applications can be connected:
```
juju add-relation redis sensu-base
juju add-relation rabbitmq-server sensu-base
```
When Sensu-base is complety setup, the rabbitmq-server password will be visible in its status message (of the Sensu-base). This password is needed for the monitoring-api config.
```
juju config monitoring-api password="[See juju status message from sensu-base]"
juju add-relation monitoring-api sojobo-api
juju add-relation monitoring-api sensu-base
juju add-relation monitoring-api influxdb
```
# Bugs
Report bugs on <a href="https://github.com/Qrama/monitoring-api/issues">Github</a>

# Author
Mathijs Moerman <a href="mailto:mathijs.moerman@tengu.io">mathijs.moerman@tengu.io</a>
