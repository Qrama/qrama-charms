# Overview

This interface layer handles the communication between Apache Spark and its
clients. The provider of this interface provides Spark services.
The consumer requires the existence of a provider to function.


# Usage

## Provides

Charms providing Apache Spark services *provide* this interface. This
interface layer will set the following states, as appropriate:

  * `{relation_name}.joined` The provider has been related to a client. At this
  point, the provider should broadcast details that clients might need:

    * If Spark is ready to process client jobs:
        * `set_spark_started()`
        * `send_master_info(master_url, master_ip)`
        * `send_rest_port(port)`
    * If Spark is not ready (e.g. Spark is in YARN mode, but YARN is not ready):
        * `clear_spark_started()`

Spark provider example:

```python
@when('spark.started', 'client.joined')
def serve_client(client):
    client.set_spark_started()
    client.send_master_info(get_master_url(), get_master_ip())
    client.send_rest_port(6066)

@when('client.joined')
@when_not('spark.started')
def stop_serving_client(client):
    client.clear_spark_started()
```

## Requires

Clients *require* this interface to connect to Apache Spark. This interface
layer will set the following states, as appropriate:

  * `{relation_name}.joined` The client charm has been related to a Spark
  provider. At this point, the charm waits for Spark configuration details.

  * `{relation_name}.master`  The provider has supplied both a Spark Master
  URL as well as a Spark Master IP address.

  * `{relation_name}.ready`  The provider has called `set_spark_started`,
  signifying Spark is ready for clients. The client charm should get Spark
  configuration details using:
    * `get_master_info()` returns a dict with the Spark Master URL and IP:
          {connection_string: 'spark://xxx.xxx.xxx.xxx:7077',
           master: 'xxx.xxx.xxx.xxx'}
    * `get_master_url()` returns the Spark Master URL used by the provider
    * `get_master_ip()` returns the IP address of the provider

Spark client example:

```python
@when('spark.joined')
@when_not('spark.ready')
def wait_for_spark(spark):
    hookenv.status_set('waiting', 'Waiting for Spark to become available')

@when('spark.ready')
@when_not('myservice.configured')
def configure(spark):
    configure_my_service(spark_master=spark.get_master_url())
    set_state('myservice.configured')
```


# Contact Information

- <bigdata@lists.ubuntu.com>
