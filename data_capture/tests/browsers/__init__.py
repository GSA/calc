import os

from .robobrowser import RoboBrowserTestCase
from .selenium import SeleniumTestCase


if 'TEST_WITH_ROBOBROWSER' in os.environ:
    BrowserTestCase = RoboBrowserTestCase
else:
    BrowserTestCase = SeleniumTestCase
