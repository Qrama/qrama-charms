# pylint: disable=c0111,c0301,c0325,c0103,r0204,r0913,r0902
import json
import requests

URL = 'http://localhost:5000'

USERS = {'admin': 'admin', 'testing': 'testing'}
APIDIR = requests.get(URL).json()['message']['api_dir']

with open('{}/api-key'.format(APIDIR), 'r') as key:
    APIKEY = key.readlines()[0]

def lvl1():
    print('\033[94m\033[1mChoose functionality:\033[0m')
    print('[1] tengu ping')
    print('[2] Es model')
    print('\033[91m\033[1m[Exit]\033[0m')
    print('Choice: ')
    return input()
def con_lvl2():
    print('\033[94m\033[1mEs-model\033[0m')
    print('Choose request:')
    print('\t[1]: Get all info')
    print('\t[2]: application')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()
def app_lvl3():
    print('\033[94m\033[1mApplication\033[0m')
    print('Choose request:')
    print('\t[1]: Juju Gui ')
    print('\t[2]: wordpress')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()

def send_ping_request():
    url = '{}/monitoring/ping'.format(URL)
    charm_ip = '10.132.30.113'
    body = {
        'api-key' : APIKEY,
        'charm-ip' : charm_ip,
        'service-name' : 'aws-sepa-est'
        }
    print(json.dumps(body))
    request = requests.put(url, data=json.dumps(body), headers={'Content-Type':'application/json'})
    return request

def get_model_monitor():
    url = '{}/monitoring/{}/{}'.format(URL, 'aws', 'sepa')
    myparams = {'api-key' : APIKEY}
    request = requests.get(url, params=myparams, auth=('admin', USERS['admin']))
    print(request)
    return request

def get_model_monitor_application(application):
    url = '{}/monitoring/{}/{}/{}/{}'.format(URL, 'aws', 'sepa', 'application', application)
    myparams = {'api-key' : APIKEY}
    request = requests.get(url, params=myparams, auth=('admin', USERS['admin']))
    return request

if __name__ == '__main__':
    while True:
        usrinp = lvl1()
        if usrinp == '1':
            res = send_ping_request()
            print(res.url)

        elif usrinp == '2':
            while True:
                usrinp = con_lvl2()
                if usrinp == '1':
                    res = get_model_monitor()
                    print(res.url)
                    print(res.text)
                elif usrinp == '2':
                    while True:
                        usrinp = app_lvl3()
                        if usrinp == '1':
                            res = get_model_monitor_application('juju-gui')
                        elif usrinp == '2':
                            res = get_model_monitor_application('wordpress')
                        elif usrinp == 'Back':
                            break
                        else:
                            print('\033[91m\033[1mInvalid input, try again!\033[0m')
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')

        elif usrinp == 'Exit':
            break
        else:
            print('\033[91m\033[1mInvalid input, try again!\033[0m')
