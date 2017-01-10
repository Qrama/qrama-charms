# pylint: disable=c0111,c0301,c0325,c0103,r0204,r0913,r0902,r0903,w1503
import os
from subprocess import check_call, CalledProcessError
import unittest
from api.controller_gce import get_supported_series, create_credentials_file, create_controller


class TestAWS(unittest.TestCase):
    def test_1_create_credentials_file(self):
        create_credentials_file('/tmp/google-unittesting.json')
        path = '/tmp/credentials.yaml'
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        os.remove('/tmp/credentials.yaml')

    def test_2_create_controller(self):
        try:
            check_call(['juju', 'destroy-controller', 'unittesting', '-y'])
        except CalledProcessError:
            pass
        try:
            check_call(['juju', 'remove-credential', 'google', 'admin'])
        except CalledProcessError:
            pass
        try:
            create_controller('unittesting', 'eu-west-1', '-f', '/tmp/google-unittesting.json')
            self.assertTrue(True)
        except CalledProcessError:
            self.assertTrue(False)
        try:
            check_call(['juju', 'destroy-controller', 'unittesting', '-y'])
        except CalledProcessError:
            pass
        try:
            check_call(['juju', 'remove-credential', 'google', 'admin'])
        except CalledProcessError:
            pass
        os.remove('/tmp/credentials.yaml')


    def test_3_get_supported_series(self):
        self.assertIsInstance(get_supported_series(), list)


if __name__ == '__main__':
    unittest.main()
