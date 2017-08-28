# Monitoring-API Documentation

The monitoring-API provides and endpoint to request and start monitoring of deployed applications.

**Currently, all the calls must be made with BasicAuth in the request!**

## API Calls
- [/monitoring](#status)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]](#application)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unitnr]](#unit)
## **/monitoring** <a name="status">
#### **Request type**: GET
* **Description**:
  Returns the status of the monitoring setup. This will be expanded to the status of the entire Tengu setup
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Successful response**:
  - code: 200
  - message:
  ```json
    {
      "Sensu": {
        "Sensu-api": "RUNNING",
        "Sensu-server": "RUNNING",
        "Sensu-Reddis-connection": "RUNNING",
        "Sensu-RabbitMQ-connection": "RUNNING"
    },
    "InfluxDB": {
      "InfluxDB": "RUNNING",
      "Parser": "RUNNING",
      "RabbitMQ": "RUNNING",
      "Redis": "RUNNING"
    }
  }
  ```
## **/monitoring/controllers/[controller]/models/[model]/applications/[application]** <a name="application"></a>
#### **Request type**: GET
* **Description**:
  Returns all the monitoring data of a single application
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Successful response**:
  - code: 200
  - message:
  ```json
    {
      "application": "mysql",
      "units": {
        "0": {
          "cpu_load": [
            {
              "time": "2017-08-25T14:02:46Z",
              "application": "mysql",
              "charm": "mysql",
              "controller": "test",
              "machine": "0",
              "model": "default",
              "name": "used",
              "size": "%", "value": 0
            }
          ]
        }
      }
    }
  ```
#### **Request type**: PUT
* **Description**:
  Adds monitoring to an application
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Successful response**:
  - code: 200
  - message:
  ```json
    "OK"
  ```
#### **Request type**: DELETE
* **Description**:
  Removes monitoring of an application. Does not remove the already collected data!
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Successful response**:
  - code: 200
  - message:
  ```json
    "OK"
  ```
## **/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unitnr]** <a name="unit"></a>
#### **Request type**: GET
* **Description**:
  Gets the monitoring information of a single unit
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Successful response**:
  - code: 200
  - message:
  ```json
    {
      "0": {
        "cpu_load": [
          {
            "time": "2017-08-25T14:02:46Z",
            "application": "mysql",
            "charm": "mysql",
            "controller": "test",
            "machine": "0",
            "model": "default",
            "name": "used",
            "size": "%",
            "unit": "0",
            "value": 0
          }
        ]
      }
    }
  ```
