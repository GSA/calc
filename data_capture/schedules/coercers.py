import re
import string

from contracts.models import EDUCATION_CHOICES
from .base import hour_regex


def strip_non_numeric(text):
    '''
    Returns a string of the given argument with non-numeric characters removed

    >>> strip_non_numeric('  $1,015.25  ')
    '1015.25'

    If a non-string argument is given, it is returned as is

    >>> strip_non_numeric(55.25)
    55.25

    '''
    if not isinstance(text, str):
        return text

    return re.sub("[^\d\.]", "", text)


def strip_punctuation_and_lower(s):
    '''
    Helper to remove punctuation and lowercase the given input

    >>> strip_punctuation_and_lower('@!.HELLO, Friend!!!!')
    'hello friend'
    '''
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in s if ch not in exclude).lower()
    return s


def gen_sublists(arr, size):
    '''
    Generator that yields sequential sublists of the specified size from the
    given list.

    >>> list(gen_sublists([1, 2, 3, 4, 5], 2))
    [[1, 2], [2, 3], [3, 4], [4, 5]]

    If the size is larger than the length of the given list, an empty list
    is generated.

    >>> list(gen_sublists(['a'], 3))
    []

    >>> list(gen_sublists([1, 2, 3], 3))
    [[1, 2, 3]]
    '''
    if size <= 0:
        raise ValueError
    arr_len = len(arr)
    for i in range(arr_len):
        if i + size <= arr_len:
            yield arr[i:i + size]


def extract_min_education(text):
    '''
    Attempts to find a valid Education Choice within the given text argument
    If a matching Education Choice is found, it is returned

    >>> extract_min_education("Bachelor's Degree")
    'Bachelors'

    >>> extract_min_education("A High School Diploma")
    'High School'

    It is biased toward the lowest level of education found in the given text

    >>> extract_min_education("Bachelors Degree or High School Diploma")
    'High School'

    If a matching Education Choice is not found, the original arg is returned

    >>> extract_min_education('BOOP')
    'BOOP'

    Matches must be found on whitespace boundaries only

    >>> extract_min_education("ABCbacherlorsXYZ")
    'ABCbacherlorsXYZ'

    >>> extract_min_education("high XYZ school")
    'high XYZ school'

    >>> extract_min_education("GED or high school")
    'High School'

    If a non-string argument is given, it is returned as is

    >>> extract_min_education(101)
    101
    '''
    if not isinstance(text, str):
        return text

    # first remove all punctuation, make lowercase, and split on whitespace
    stripped_and_split_text = strip_punctuation_and_lower(text).split()

    # generate a list of tuples of the form
    # (education choice, stripped-lowered-split education choice)
    desired = [(label, strip_punctuation_and_lower(label).split())
               for _, label in EDUCATION_CHOICES]

    # for each stripped-lowered-split education choice
    for label, stripped_and_split_label in desired:
        # find and return the first one that matches an equally-sized sublist
        # of the stripped_and_split_text
        for sublist in gen_sublists(stripped_and_split_text,
                                    len(stripped_and_split_label)):
            if stripped_and_split_label == sublist:
                return label

    return text


def extract_hour_unit_of_issue(text):
    '''
    Returns 'Hour' if the given text matches
    'Hour' or 'Hourly' (case-insensitive)

    >>> extract_hour_unit_of_issue('Hourly')
    'Hour'

    >>> extract_hour_unit_of_issue('hour')
    'Hour'

    >>> extract_hour_unit_of_issue('  hourly  ')
    'Hour'

    Returns the original string if it does not match

    >>> extract_hour_unit_of_issue('boop')
    'boop'

    Returns the original value if the input is not a string

    >>> extract_hour_unit_of_issue(50)
    50
    '''
    if not isinstance(text, str) or not hour_regex.match(text.strip()):
        return text

    return 'Hour'


def extract_first_int(text):
    '''
    Returns the first integer found in the input text.

    >>> extract_first_int('At least 12 years with 8 years management')
    12

    >>> extract_first_int('5+')
    5

    >>> extract_first_int(8.0)
    8

    Returns the original value if an integer is not found.

    >>> extract_first_int('No integers here')
    'No integers here'
    '''
    match = re.search(r'\d+', str(text))
    if not match:
        return text

    return int(match.group())
