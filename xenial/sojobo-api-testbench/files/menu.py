# pylint: disable=c0111,c0301,c0325,c0103,r0204,r0913,r0902
import requests


USERS = {'admin': 'admin', 'testing': 'testing'}
URL = 'http://localhost:5000'
APIDIR = requests.get(URL).json()['message']['api_dir']
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
    print('\t[1]: Get machine information')
    print('\t[2]: Create machine')
    print('\t[3]: Delete machine')
    print('\033[91m\033[1m[Back]\033[0m')
    print('Choice: ')
    return input()


def rel_lvl2():
    print('\033[94m\033[1mRelations\033[0m')
    print('Choose request:')
    print('\t[1]: Create relation between applications')
    print('\t[2]: Get relation info of an application')
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


if __name__ == '__main__':
    while True:
        usrinp = lvl1()
        if usrinp == '1':
            while True:
                usrinp = con_lvl2()
                if usrinp == '1':
                    result = requests.get('{}/tengu/controllers'.format(URL), params={'api_key': APIKEY}, auth=('admin', USERS['admin']))
                    print(result.url)
                    print(result.text)
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
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
        elif usrinp == '2':
            while True:
                usrinp = mod_lvl2()
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
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
        elif usrinp == '3':
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
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
        elif usrinp == '4':
            while True:
                usrinp = mac_lvl2()
                if usrinp == '1':
                    pass
                elif usrinp == '2':
                    pass
                elif usrinp == '3':
                    pass
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
        elif usrinp == '5':
            while True:
                usrinp = rel_lvl2()
                if usrinp == '1':
                    pass
                elif usrinp == '2':
                    pass
                elif usrinp == '3':
                    pass
                elif usrinp == 'Back':
                    break
                else:
                    print('\033[91m\033[1mInvalid input, try again!\033[0m')
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
