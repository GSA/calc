from itertools import chain, combinations
from functools import cmp_to_key
from collections import OrderedDict

try:
    import nltk
    nltk.data.path.append('nltk_data')
    nltk.data.path.append('../nltk_data')
except ImportError:
    nltk = None

from django.db import connection

from contracts.models import Contract


# Minimum number of times a word must appear across all contract labor
# categories for it to be added to the vocabulary.
DEFAULT_MIN_NDOC = 4


# List of words that are, for all intents and purposes, "stop words"
# with respect to price list analysis. Any alphabetic characters should
# be lowercase.
ANALYSIS_STOP_WORDS = []


# Cap on number of lexemes that get_best_permutations will process.
# This is a crude attempt to stop the CPU/RAM consumption of the function from
# getting too large.
MAX_LEXEMES_FOR_PERMUTATIONS = 8


# http://stackoverflow.com/a/28777781
def write_roman(num):
    roman: OrderedDict[int, str] = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])


for i in range(1, 10):
    ANALYSIS_STOP_WORDS.append(write_roman(i).lower())
    ANALYSIS_STOP_WORDS.append(str(i))
del i


# https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def get_best_permutations(vocab, lexemes, min_count=1, min_length=4,
                          max_permutations=8):
    def compare(a, b):
        a_len = len(a)
        b_len = len(b)

        if a_len != b_len:
            return a_len - b_len

        return vocab_val(a) - vocab_val(b)

    def vocab_val(iterable):
        if len(iterable) == 1:
            return vocab[iterable[0]]
        upper_bound = float('inf')
        for a, b in combinations(iterable, 2):
            c = vocab.get_cooccurrences(a, b)
            if c < upper_bound:
                upper_bound = c
        return upper_bound

    def are_cooccurrences_valid(lexemes):
        for a, b in combinations(lexemes, 2):
            if vocab.get_cooccurrences(a, b) < min_count:
                return False
        return True

    # Impose a mex length on the number of lexemes:
    safer_lexemes = lexemes[:MAX_LEXEMES_FOR_PERMUTATIONS]
    # Remove the first element, as it's the empty set.
    permutations = list(powerset(safer_lexemes))[1:]

    permutations = list(filter(
        lambda x: len(' '.join(x)) >= min_length,
        permutations
    ))
    permutations = list(filter(are_cooccurrences_valid, permutations))
    permutations.sort(key=cmp_to_key(compare), reverse=True)

    return permutations[:max_permutations]


class Vocabulary(dict):
    def __init__(self):
        super()
        self._cinfo = {}  # type: ignore

    @classmethod
    def from_list(cls, docs):
        vocab = cls()
        for doc in docs:
            words = doc.split()
            for word in words:
                if word not in vocab:
                    vocab[word] = 0
                vocab[word] += 1
            vocab._update_cooccurrence_info(words)
        return vocab

    @classmethod
    def from_db(cls, cursor, model=Contract, field='search_index',
                min_ndoc=DEFAULT_MIN_NDOC):
        tsvector_query = 'select {} from {}'.format(
            model._meta.get_field(field).column,
            model._meta.db_table
        )
        cursor.execute(
            "select word, ndoc from ts_stat(%s) WHERE ndoc >= %s",
            [tsvector_query, min_ndoc]
        )
        vocab = cls()
        for word, ndoc in cursor.fetchall():
            vocab[word] = ndoc
        vocab._init_cooccurrence_info_from_db(cursor, model, field)
        return vocab

    def get_cooccurrences(self, a, b):
        return self._cinfo.get(a, {}).get(b, 0)

    def _update_cooccurrence_info(self, lexemes):
        cinfo = self._cinfo
        lexemes = [lexeme for lexeme in lexemes if lexeme in self]
        for lexeme in lexemes:
            if lexeme not in cinfo:
                cinfo[lexeme] = {}
            lexeme_cinfo = cinfo[lexeme]
            for other_lexeme in lexemes:
                lexeme_cinfo[other_lexeme] = lexeme_cinfo.get(
                    other_lexeme,
                    0
                ) + 1

    def _init_cooccurrence_info_from_db(self, cursor, model, field):
        with connection.cursor() as cursor:
            cursor.execute('select strip({}) from {}'.format(
                model._meta.get_field(field).column,
                model._meta.db_table
            ))

            for (search,) in cursor:
                lexemes = [lexeme[1:-1] for lexeme in search.split(' ')]
                self._update_cooccurrence_info(lexemes)


def get_lexemes(cursor, words, cache):
    uncached_words = [word for word in words if word not in cache]
    if uncached_words:
        cursor.execute(
            "select {}".format(
                ', '.join(["plainto_tsquery(%s)"] * len(words))
            ),
            words
        )
        lexemes = [column[1:-1] for column in cursor.fetchone()]
        for word, lexeme in zip(words, lexemes):
            cache[word] = lexeme
    return [cache[word] for word in words]


def filter_and_sort_lexemes(vocab, lexemes):
    lexemes = [lexeme for lexeme in lexemes if lexeme in vocab]
    lexemes.sort(
        key=lambda x: vocab[x],
        reverse=True
    )
    return lexemes


class PartOfSpeechMapper:
    def __init__(self, words):
        self._tags = {}  # type: ignore
        if nltk is not None:
            self._tags.update(dict(nltk.pos_tag(
                [word.lower() for word in words] +
                # NLTK's POS tagger expects full sentences, whereas the
                # words we've been given really just represent a noun, so
                # we'll use them as the subject of a sentence.
                ['jumps', 'over', 'the', 'lazy', 'dog', '.']
            )))

    def contains_noun(self, words):
        pos_types = [self._tags.get(word.lower(), 'NN') for word in words]
        for pos_type in pos_types:
            if pos_type.startswith('NN'):
                return True
        return False


def broaden_query(cursor, vocab, query, cache, min_count):
    '''
    Return an iterator that yields subsets of the given query; the
    subsets are defined by removing search terms in order of the number of
    documents they appear in, with the most uncommon terms being removed
    first.
    '''

    orig_words = [
        word for word in query.split()
        if word.lower() not in ANALYSIS_STOP_WORDS
    ]
    orig_word_ordering = dict(zip(orig_words, range(len(orig_words))))
    orig_lexemes = get_lexemes(cursor, orig_words, cache)
    word_map = dict(zip(orig_lexemes, orig_words))
    lexemes_in_vocab = [lexeme for lexeme in orig_lexemes if lexeme in vocab]
    pos_mapper = PartOfSpeechMapper(orig_words)

    # Always yield the query verbatim. This way if the POS mapper thinks
    # the query has no nouns in it, e.g. "Clerical I", at least we still do
    # at least one search for it.
    yield ' '.join(orig_words)

    for lexemes in get_best_permutations(vocab, lexemes_in_vocab, min_count):
        words = sorted(
            [word_map[lexeme] for lexeme in lexemes],
            key=lambda word: orig_word_ordering[word]
        )
        if pos_mapper.contains_noun(words):
            yield ' '.join(words)
