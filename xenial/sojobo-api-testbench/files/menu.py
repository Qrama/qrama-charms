# pylint: disable=c0111,c0301,c0325,c0103,r0204,r0913,r0902
from datetime import datetime
import requests


USERS = {'admin': 'admin', 'testing': 'testing'}
URL = 'http://localhost:5000'
APIDIR = requests.get(URL).json()['message']['api_dir']
SSH_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsYMJGNGG74HAJha3n2CFmWYsOOaORnJK6VqNy86pj0MIpvRXBzFzVy09uPQ66GOQhTEoJHEqE77VMui7+62AcMXT+GG7cFHcnU8XVQsGM6UirCcNyWNysfiEMoAdZScJf/GvoY87tMEszhZIUV37z8PUBx6twIqMdr31W1J0IaPa+sV6FEDadeLaNTvancDcHK1zuKsL39jzAg7+LYjKJfEfrsQP+lj/EQcjtKqlhVS5kzsJVfx8ZEd0xhW5G7N6bCdKNalS8mKCMaBXJpijNQ82AiyqCIDCRrre2To0/i7pTjRiL0U9f9mV3S4NJaQaokR050w/ZLySFf6F7joJT mathijs@Qrama-Mathijs'
with open('{}/api-key'.format(APIDIR), 'r') as key:
    APIKEY = key.readlines()[0]


def lvl1():
    print('\033[94m\033[1mChoose functionality:\033[0m')
    print('[1] Controllers')
    print('[2] Models')
    print('[3] Applications')
    print('[4] Machines')
    print('[5] Relations')
    print('[6] Users')
    print('\033[91m\033[1m[Exit]\033[0m')
    print('Choice: ')
    return input()


def con_lvl2():
    print('\033[94m\033[1mControllers\033[0m')
    print('Choose request:')
    print('\t[1]: Get all info')
    print('\t[2]: Create controller')
    print('\t[3]: Get info of one controller')
    print('\t[4]: Delete controller')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def mod_lvl2():
    print('\033[94m\033[1mModels\033[0m')
    print('Choose request: ')
    print('\t[1]: Create model')
    print('\t[2]: Get model info')
    print('\t[3]: Delete model')
    print('\t[4]: Add ssh-key to model')
    print('\t[5]: Remove ssh-key from model')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def app_lvl2():
    print('\033[94m\033[1mApplications\033[0m')
    print('Choose request:')
    print('\t[1]: Get application info')
    print('\t[2]: Create application')
    print('\t[3]: Delete application')
    print('\t[4]: Add monitoring to model')
    print('\t[5]: Add unit to application')
    print('\t[6]: Remove unit from application')
    print('\t[7]: Get unit info')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def mac_lvl2():
    print('\033[94m\033[1mMachines\033[0m')
    print('Choose request:')
    print('\t[1]: Get machines information')
    print('\t[2]: Get machine information')
    print('\t[3]: Create machine')
    print('\t[4]: Delete machine')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def rel_lvl2():
    print('\033[94m\033[1mRelations\033[0m')
    print('Choose request:')
    print('\t[1]: Get relation info of an application')
    print('\t[2]: Create relation between applications')
    print('\t[3]: Remove relation between two applications')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def use_lvl2():
    print('\033[94m\033[1mUsers\033[0m')
    print('Choose request:')
    print('\t[1]: Get all users info')
    print('\t[2]: Create user')
    print('\t[3]: Get user info')
    print('\t[4]: Delete user')
    # print('\t[5]: Make user admin')
    print('\t[5]: Add user to controller')
    print('\t[6]: Remove user from controller')
    print('\t[7]: Add user to model')
    print('\t[8]: Remove user from model')
    print('\t\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def mod_input():
    print('Controller:')
    mcon = input()
    print('Model:')
    mmod = input()
    return mcon, mmod


def app_input():
    acon, amod = mod_input()
    print('Application:')
    aapp = input()
    return acon, amod, aapp


def mach_input():
    mcon, mmod = mod_input()
    print('Machine:')
    mmach = input()
    return mcon, mmod, mmach


if __name__ == '__main__':
    while True:
        usrinp = lvl1()
        if usrinp == '1':
            while True:
                usrinp = con_lvl2()
                if usrinp == '1':
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers'.format(URL),
                                          headers={'api-key': APIKEY},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '2':
                    print('Enter Type, supported types are [google, aws, maas] : ')
                    while True:
                        t = input()
                        if t in ['google', 'aws', 'maas']:
                            break
                        else:
                            print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    print('Enter Region:')
                    region = input()
                    print('Enter Name:')
                    name = input()
                    if t == 'google':
                        a = datetime.now()
                        result = requests.post('{}/tengu/controllers'.format(URL),
                                               headers={'api-key': APIKEY},
                                               data={'type': t, 'region': region, 'controller': name},
                                               files={'file': ('qrama.json', open('/home/ubuntu/qrama.json', 'rb'), 'application/json')},
                                               auth=('admin', USERS['admin']))
                        b = datetime.now()
                    elif t == 'maas':
                        a = datetime.now()
                        result = requests.post('{}/tengu/controllers'.format(URL),
                                               headers={'api-key': APIKEY},
                                               json={'type': t, 'region': region, 'controller': name, 'credentials': {}},
                                               auth=('admin', USERS['admin']))
                        b = datetime.now()
                    elif t == 'aws':
                        a = datetime.now()
                        result = requests.post('{}/tengu/controllers'.format(URL),
                                               headers={'api-key': APIKEY},
                                               json={'type': t, 'region': region, 'controller': name, 'credentials': {'access-key': 'AKIAJ73LUJYI2GG4AGKQ', 'secret-key': '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'}},
                                               auth=('admin', USERS['admin']))
                        b = datetime.now()
                elif usrinp == '3':
                    print('Controller:')
                    con = input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}'.format(URL, con),
                                          headers={'api-key': APIKEY},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '4':
                    print('Controller:')
                    con = input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}'.format(URL, con),
                                             headers={'api-key': APIKEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    break
                print(result.url)
                print(result.text)
                delta = b-a
                print('Time: {} ms'.format(delta.total_seconds()*1000))
        elif usrinp == '2':
            while True:
                usrinp = mod_lvl2()
                if usrinp == '1':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.put('{}/tengu/controllers/{}'.format(URL, con),
                                          headers={'api-key': APIKEY},
                                          json={'model': mod},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '2':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}'.format(URL, con, mod),
                                          headers={'api-key': APIKEY},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '3':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}'.format(URL, con, mod),
                                             headers={'api-key': APIKEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '4':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.post('{}/tengu/controllers/{}/models/{}/sshkey'.format(URL, con, mod),
                                           headers={'api-key': APIKEY},
                                           json={'ssh_key': SSH_KEY},
                                           auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '5':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}/sshkey'.format(URL, con, mod),
                                             headers={'api-key': APIKEY},
                                             json={'ssh_key': SSH_KEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    break
                print(result.url)
                print(result.text)
                delta = b-a
                print('Time: {} ms'.format(delta.total_seconds()*1000))
        elif usrinp == '3':
            while True:
                usrinp = app_lvl2()
                if usrinp == '1':
                    con, mod, app = app_input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}/applications/{}'.format(URL, con, mod, app),
                                          headers={'api-key': APIKEY},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '2':
                    con, mod, app = app_input()
                    a = datetime.now()
                    result = requests.post('{}/tengu/controllers/{}/models/{}/applications'.format(URL, con, mod),
                                           headers={'api-key': APIKEY},
                                           json={'application': app},
                                           auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '3':
                    con, mod, app = app_input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}/applications/{}'.format(URL, con, mod, app),
                                             headers={'api-key': APIKEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '4':
                    pass
                elif usrinp == '5':
                    con, mod, app = app_input()
                    a = datetime.now()
                    result = requests.post('{}/tengu/controllers/{}/models/{}/applications/{}/units'.format(URL, con, mod, app),
                                           headers={'api-key': APIKEY},
                                           auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '6':
                    con, mod, app = app_input()
                    print('Unit:')
                    unit = input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}/applications/{}/units/{}'.format(URL, con, mod, app, unit),
                                             headers={'api-key': APIKEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '7':
                    con, mod, app = app_input()
                    print('Unit:')
                    unit = input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}/applications/{}/units/{}'.format(URL, con, mod, app, unit),
                                          headers={'api-key': APIKEY},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    break
                print(result.url)
                print(result.text)
                delta = b-a
                print('Time: {} ms'.format(delta.total_seconds()*1000))
        elif usrinp == '4':
            while True:
                usrinp = mac_lvl2()
                if usrinp == '1':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}/machines'.format(URL, con, mod),
                                          headers={'api-key': APIKEY}, auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '2':
                    con, mod, mach = mach_input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}/machines/{}'.format(URL, con, mod, mach),
                                          headers={'api-key': APIKEY}, auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '3':
                    con, mod = mod_input()
                    a = datetime.now()
                    result = requests.post('{}/tengu/controllers/{}/models/{}/machines/'.format(URL, con, mod),
                                           headers={'api-key': APIKEY}, auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '4':
                    con, mod, mach = mach_input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}/machines/{}'.format(URL, con, mod, mach),
                                             headers={'api-key': APIKEY}, auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    break
                print(result.url)
                print(result.text)
                delta = b-a
                print('Time: {} ms'.format(delta.total_seconds()*1000))
        elif usrinp == '5':
            while True:
                usrinp = rel_lvl2()
                if usrinp == '1':
                    con, mod, app = app_input()
                    a = datetime.now()
                    result = requests.get('{}/tengu/controllers/{}/models/{}/relations/{}'.format(URL, con, mod, app),
                                          headers={'api-key': APIKEY}, auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '2':
                    con, mod, app1 = app_input()
                    print('Second application:')
                    app2 = input()
                    a = datetime.now()
                    result = requests.put('{}/tengu/controllers/{}/models/{}/relations/'.format(URL, con, mod),
                                          headers={'api-key': APIKEY},
                                          json={'app1': app1, 'app2': app2},
                                          auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == '3':
                    con, mod, app1 = app_input()
                    print('Second application:')
                    app2 = input()
                    a = datetime.now()
                    result = requests.delete('{}/tengu/controllers/{}/models/{}/relations/{}/{}'.format(URL, con, mod, app1, app2),
                                             headers={'api-key': APIKEY},
                                             auth=('admin', USERS['admin']))
                    b = datetime.now()
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
                    break
                print(result.url)
                print(result.text)
                delta = b-a
                print('Time: {} ms'.format(delta.total_seconds()*1000))
        elif usrinp == '6':
            while True:
                usrinp = app_lvl2()
                if usrinp == '1':
                    pass
                elif usrinp == '2':
                    pass
                elif usrinp == '3':
                    pass
                elif usrinp == '4':
                    pass
                elif usrinp == '5':
                    pass
                elif usrinp == '6':
                    pass
                elif usrinp == '7':
                    pass
                elif usrinp == '8':
                    pass
                elif usrinp == '9':
                    pass
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
        elif usrinp == 'Exit':
            break
        else:
            print('\033[91m\033[1mInvalid input, try again!\033[0m')
