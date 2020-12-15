from .util import ProductionTestCase


def pytest_addoption(parser):
    parser.addoption('--origin', dest='origin',
                     default='https://calc.gsa.gov',
                     help='origin of production server')


def pytest_configure(config):
    ProductionTestCase.ORIGIN = config.getvalue('origin')
