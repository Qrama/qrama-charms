# Monitoring-API Documentation

the monitoring api is deployed as a blueprint on top of the Sojobo-api and can be deployed and removed by using the monitoring-api charm. The monitoring consists of a few API Calls that can be accessed on the some IP and port as the Sojobo-Api. 

## API Calls 
- [/monitoring/ping](#ping)
- [/monitoring/controllers/[controller]/models/[model]](#model)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]](#application)
- [/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unit_nr]](#unit)

## **/monitoring/ping** <a name="ping"></a>
* **Request type**: PUT
* **Required headers**:
  - api-key
  - Content-Type:application/json
* **Required body**:
  - charm-ip
  - service-name
* **succesfull response**:
  - code: 200
  - message: `succesfully connected to SOJOBO-api`
* **description**: 
  - This call will register the Ip adress and the service name of the charm that wants to connect the sojobo-api. This call only needs to be used by Tengu Charms like the <a href="https://github.com/Qrama/elasticsearch-tengu">`elasticsearch-tengu` charm </a>
* **Python example**:
```Python
def send_request_to_sojobo(sojobo_ip, api_key, charm_ip)
    url = 'http://{}:5000/monitoring/ping'.format(sojobo_ip)
    body = {
        'charm-ip' : charm_ip,
        'service-name' : service_name()
        }
    myheaders = {'Content-Type':'application/json', 'api-key' : api_key}
    res = requests.put(url, data=json.dumps(body), headers=myheaders)
```

## **/monitoring/controllers/[controller]/models/[model]** <a name="model"></a>
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
* **description**: 
  - This call will return all the monitoring information about the [model] from a specific [controller]. Basic auth will check if the user has acces to that controller and model. 
* **Python example**:
```Python
def get_model_monitor(api_key):
    url = '{}/monitoring/controllers/{}/models/{}'.format(URL, 'aws', 'default')
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```

## **/monitoring/controllers/[controller]/models/[model]/applications/[application]** <a name="application"></a>
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
* **description**: 
  - This call will return all the monitoring information about the specified [application] in that [model] from a specific [controller]. Basic auth will check if the user has acces to that controller and model. 
* **Python example**:
```Python
def get_model_monitor_application(application, api_key):
    url = '{}/monitoring/controllers/{}/models/{}/applications/{}'.format(URL, 'aws', 'default', application)
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```

## **/monitoring/controllers/[controller]/models/[model]/applications/[application]/units/[unit_nr]** <a name="unit"></a>
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
* **description**: 
  - This call will return all the monitoring information about a specific unit from an application. [unit_nr] is an integer that will decide which unit has to be monitored. Basic auth will check if the user has acces to that controller and model.
* **Python example**:
```Python
def get_model_monitor_unit(application, unitnr, api_key):
    url = '{}/monitoring/controllers/{}/models/{}/applications/{}/unit/{}'.format(URL, 'aws', 'default', application, unitnr)
    myheaders = {'api-key' : api_key}
    request = requests.get(url, headers=myheaders, auth=('admin', USERS['admin']))
    return request
```
