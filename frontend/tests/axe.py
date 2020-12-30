'''
    This module provides functionality to validate the accessibility
    properties of a web page using WebDriver and aXe-core.

    For more details on aXe, see https://www.deque.com/products/axe/.
'''

from pathlib import Path
import pprint

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

AXE_JS = ROOT_DIR / 'node_modules' / 'axe-core' / 'axe.js'

IGNORED_VIOLATIONS = [
    # We should eventually enable these, but for now we'll disable
    # them because it's easier. Better *some* a11y testing than none
    # at all!
    'color-contrast',
]

axe_js = None


def get_axe_js():
    '''
    Return the contents of the aXe-core JavaScript.
    '''

    global axe_js

    if axe_js is None:
        axe_js = AXE_JS.read_text()

    return axe_js


def run_and_validate(webdriver):
    '''
    Run aXe-core on the current web page loaded by the given
    WebDriver instance. Raise an exception if there are any
    accessibility issues with the page and log any violations to
    stdout.
    '''

    options = {
        "rules": {},
    }

    for rule_name in IGNORED_VIOLATIONS:
        options['rules'][rule_name] = {'enabled': False}

    result = webdriver.execute_async_script(
        get_axe_js() +
        r'''
        var options = arguments[0];
        var callback = arguments[arguments.length - 1];
        axe.run(options, function(err, results) {
          callback({
            error: err && err.toString(),
            results: results
          });
        });
        ''', options)

    error = result['error']
    if error is not None:
        raise Exception(f'axe.run() failed: {error}')

    violations = result['results']['violations']
    if violations:
        pprint.pprint(violations)
        print("For more details, please install the aXe browser extension.")
        print("Learn more at: https://www.deque.com/products/axe/")

        raise Exception('axe.run() found violations: ' +
                        ', '.join(v['id'] for v in violations))
