import os
from unittest import TestCase
import json
import yaml

from semantic_version import Version
from django.conf import settings

MY_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.normpath(os.path.join(MY_DIR, '..', '..'))


def path(*x):
    return os.path.join(ROOT_DIR, *x)


class PythonVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify the
    same Python version.
    '''

    # We only need to use down to the minor version specifier.
    python_version = '3.6'

    def test_runtime_txt(self):
        with open(path('runtime.txt')) as f:
            self.assertEqual(
                f.read().strip(),
                f'python-{self.python_version}.x')

    def test_dockerfile(self):
        with open(path('Dockerfile')) as f:
            # We specify the patch version in our Dockerfile, but this
            # test will just check down to the minor version level
            self.assertIn(f'FROM python:{self.python_version}', f.read())

    def test_circle_yml(self):
        with open(path('.circleci/config.yml')) as f:
            data = yaml.safe_load(f)
            self.assertEqual(
                str(data['jobs']['build']['docker'][0]['image']),
                f'circleci/python:{self.python_version}-browsers')


class PostgresVersionTests(TestCase):

    version = Version(settings.POSTGRES_VERSION)

    def test_docker_compose_yml(self):
        with open(path('docker-compose.yml')) as f:
            self.assertIn(f"image: postgres:{self.version}", f.read())

    def test_circle_yml(self):
        with open(path('.circleci/config.yml')) as f:
            data = yaml.safe_load(f)
            # In Circle we can only specify down to the minor number
            self.assertEqual(
                str(data['jobs']['build']['docker'][1]['image']),
                f"circleci/postgres:{self.version.major}.{self.version.minor}")


class NodeVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify
    the same Node version.
    '''

    version = Version('6.14.4', partial=True)

    def test_package_json(self):
        with open(path('package.json')) as f:
            package = json.load(f)
            min_version = package['engines']['node'].split()[0]
            self.assertEqual(min_version, f'>={self.version}')
