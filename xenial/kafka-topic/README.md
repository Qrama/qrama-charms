# Overview
This charm will Add a topic on Kafka. This makes it possible to directly connect
to a topic instead of first connecting to Kafka and then connecting to a topic.

To use this charm make sure you have a Kafka and Zookeeper running in your juju
model:

```
git clone https://github.com/Qrama/layer-kafka-topic
charm build layer-kafka-topic
juju deploy /path/to/kafka-topic <topic-name>
juju add-relation kafka <topic-name>
```

### maintainers
- Sébastien Pattyn <sebastien.pattyn@tengu.io>
