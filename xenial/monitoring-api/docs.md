# Monitoring-API Documentation

the monitoring api is deployed as a blueprint on top of the Sojobo-api and can be deployed and removed by using the monitoring-api charm. The monitoring consists of a few API Calls that can be accessed on the some IP and port as the Sojobo-Api.

## API Calls
- [/monitoring/ping](#ping)
- [/monitoring/controllers/[controller]/models/[model]](#model)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]](#application)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unit_nr]](#unit)

## **/monitoring/ping** <a name="ping"></a>
* **description**:
  - This call will register the Ip adress and the service name of the charm that wants to connect the sojobo-api. This call only needs to be used by Tengu Charms like the <a href="https://github.com/Qrama/elasticsearch-tengu">`elasticsearch-tengu` charm </a>
* **Request type**: PUT
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Required body**:
  - charm-ip
  - controller
  - model
* **succesfull response**:
  - code: 200
  - message: `succesfully connected to SOJOBO-api`
* **Python example**:
```Python
def send_request_to_sojobo(sojobo_ip, api_key, charm_ip):
    conf = hookenv.config()
    url = 'http://{}:5000/monitoring/ping'.format(sojobo_ip)
    body = {
        'charm-ip' : charm_ip,
        'controller' : conf['controller'],
        'model' : conf['model']
        }
    myheaders = {'Content-Type':'application/json', 'api-key' : api_key}
    res = requests.put(url, data=json.dumps(body), headers=myheaders)
```

## **/monitoring/controllers/[controller]/models/[model]** <a name="model"></a>
* **description**:
  - This call will return all the monitoring information about the [model] from a specific [controller]. Basic auth will check if the user has acces to that controller and model.
* **Request type**: GET
* **Required headers**:
  - api-key
* **Required auth**:
  - basic auth username and password
* **succesfull response**:
  - code: 200
  - response:
    - JSON:
    ```Python
    {unique_id:
      {metrics: "set of metrics"},
      {name: "hostname of machine"},
      {timestamp: "timestamp of metric"}}
    ```
* **Python example**:
```Python
def get_model_monitor(api_key):
    url = '{}/monitoring/controllers/{}/models/{}'.format(URL, 'aws', 'default')
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```

## **/monitoring/controllers/[controller]/models/[model]/applications/[application]** <a name="application"></a>
* **description**:
  - This call will return all the monitoring information about the specified [application] in that [model] from a specific [controller]. Basic auth will check if the user has access to that controller and model.
* **Request type**: GET
* **Required headers**:
  - api-key
* **Required auth**:
  - basic auth username and password
* **succesfull response**:
  - code: 200
  - response:
    - JSON:
    ```Python
    {unique_id:
      {metrics: "set of metrics"},
      {name: "hostname of machine"},
      {timestamp: "timestamp of metric"}}
    ```
## **/monitoring/controllers/[controller]/models/[model]/applications/[application]** <a name="application"></a>
* **description**:
  - This will setup the monitoring for an application.
  - If no other monitoring has been activated, this will install the required core
  - If monitoring already is active on the application, do nothing instead of failing **ToDo**
* **Request type**: PUT
* **Required headers**:
  - api-key
* **Required auth**:
  - basic auth username and password
* **succesfull response**:
  - code: 200
  - response:
  ```json
  {"name": "application name",
   "units": [{"name": "unit-name",
              "ip": "ip-address",
              "port": "used ports",
              "machine": "machine name"}],
   "relations": [{"interface": "interface-name",
                  "with": "name of the other application"}],
   "charm-name": "Name of the charm build",
   "exposed": "Whether or not the application is publicly accessible",
   "series": "Ubuntu series of the application"}
  ```
## **/monitoring/controllers/[controller]/models/[model]/applications/[application]** <a name="application"></a>
* **description**:
  - This will remove monitoring from an application
  - If no other monitoring has been activated, then the required core will be removed **ToDo**
* **Request type**: DELETE
* **Required headers**:
  - api-key
* **Required auth**:
  - basic auth username and password
* **succesfull response**:
  - code: 200
  - response:
  ```json
  {"name": "application name",
   "units": [{"name": "unit-name",
              "ip": "ip-address",
              "port": "used ports",
              "machine": "machine name"}],
   "relations": [{"interface": "interface-name",
                  "with": "name of the other application"}],
   "charm-name": "Name of the charm build",
   "exposed": "Whether or not the application is publicly accessible",
   "series": "Ubuntu series of the application"}
  ```
* **Python example**:
```Python
def get_model_monitor_application(application, api_key):
    url = '{}/monitoring/controllers/{}/models/{}/applications/{}'.format(URL, 'aws', 'default', application)
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```

## **/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unit_nr]** <a name="unit"></a>
* **description**:
  - This call will return all the monitoring information about a specific unit from an application. [unit_nr] is an integer that will decide which unit has to be monitored. Basic auth will check if the user has acces to that controller and model.
* **Request type**: GET
* **Required headers**:
  - api-key
* **Required auth**:
  - basic auth username and password
* **succesfull response**:
  - code: 200
  - response:
    - JSON:
    ```Python
    {unique_id:
      {metrics: "set of metrics"},
      {name: "hostname of machine"},
      {timestamp: "timestamp of metric"}}
    ```
* **Python example**:
```Python
def get_model_monitor_unit(application, unitnr, api_key):
    url = '{}/monitoring/controllers/{}/models/{}/applications/{}/unit/{}'.format(URL, 'aws', 'default', application, unitnr)
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```
