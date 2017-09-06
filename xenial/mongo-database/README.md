# Overview
This charm will Add a Database on MongoDB. This makes it possible to directly connect
to a DB instead of first connecting to Kafka and then connecting to a DB.


```
git clone https://github.com/Qrama/layer-mongo-database
charm build layer-mongo-database
juju deploy /path/to/mongo-database <db-name>
juju add-relation mongodb <db-name>
```

### maintainers
- Sébastien Pattyn <sebastien.pattyn@tengu.io>
