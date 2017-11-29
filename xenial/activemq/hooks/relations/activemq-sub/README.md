# ActiveMQ Interface

 This is a Juju charm interface layer. This interface is used for
 connecting to an Apache ActiveMQ unit. In order to use this interface with the ActiveMQ charm,
 this repo should be cloned into the $INTERFACE_PATH and renamed to activemq instead of interface-activemq

### Examples

#### Requires

If your charm needs to connect to ActiveMQ:

  `metadata.yaml`

```yaml
requires:
  messagebroker:
    interface: activemq
```

  `layer.yaml`

```yaml
includes: ['interface:activemq']
```  

  `reactive/code.py`

```python
@when('messagebroker.available')
def connect_to_activemq(messagebroker):
    print('{}/{}'.format(messagebroker.host(), messagebroker.port()))
)

```


#### Provides

The ActiveMQ charm can be found [here](https://github.com/Qrama/layer-activemq):

  `metadata.yaml`

```yaml
provides:
    messagebroker:
      interface: activemq
```

  `layer.yaml`

```yaml
includes: ['interface:activemq']
```

  `reactive/code.py`

```python
@when('messagebroker.available', 'activemq.installed')
@when_not('activemq.broker-configured')
def configure_broker(messagebroker):
    port_nr = config()['port']
    messagebroker.configure(port_nr)
    set_state('activemq.broker-configured')
```

# Contact Information

 - Sébastien Pattyn <sebastien.pattyn@tengu.io>
