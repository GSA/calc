import abc
from typing import Tuple, List
from django.db.models import QuerySet

from contracts.models import EDUCATION_CHOICES


QueryStringTuple = Tuple[Tuple[str, str], ...]


class ContractFinder(metaclass=abc.ABCMeta):
    '''
    Abstract base class representing a finder for contracts that match
    a certain criteria.
    '''

    def __init__(self, min_years_experience: int,
                 education_level: str) -> None:
        self.min_years_experience = min_years_experience
        self.education_level = education_level

    @abc.abstractmethod
    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        '''
        Return the given Django QuerySet with the matching criteria
        applied to it.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_data_explorer_qs_params(self) -> QueryStringTuple:
        '''
        Return a tuple of (name, value) pairs representing querystring
        arguments to pass to the Data Explorer, which will result in a
        Data Explorer URL that filters to this class' matching criteria.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_exp_comparable_search_criteria(self) -> str:
        '''
        Return a string describing, in English, the search criteria for
        finding comparables in terms of experience.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def get_edu_comparable_search_criteria(self) -> str:
        '''
        Return a string describing, in English, the search criteria for
        finding comparables in terms of education.
        '''

        raise NotImplementedError()


class ExactEduAndExpFinder(ContractFinder):
    '''
    Finds contracts that are exactly equal to a given
    education level, and around a given experience level.
    '''

    MAX_YEARS_DELTA = 4

    @property
    def max_years_experience(self) -> int:
        return self.min_years_experience + self.MAX_YEARS_DELTA

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        return qs.filter(
            min_years_experience__gte=self.min_years_experience,
            min_years_experience__lte=self.max_years_experience,
            education_level=self.education_level
        )

    def get_data_explorer_qs_params(self) -> QueryStringTuple:
        return (
            ('min_experience', str(self.min_years_experience)),
            ('max_experience', str(self.max_years_experience)),
            ('education', self.education_level),
        )

    def get_exp_comparable_search_criteria(self) -> str:
        return "{}-{} years".format(
            self.min_years_experience,
            self.max_years_experience,
        )

    def get_edu_comparable_search_criteria(self) -> str:
        return self.education_level


class GteEduAndExpFinder(ContractFinder):
    '''
    Finds contracts that are greater than or equal to a given
    minimum experience and education level.
    '''

    def get_valid_education_levels(self) -> List[str]:
        '''
        Returns a list of education levels that are equal to or
        greater than our own.
        '''

        # TODO: This code is largely copied from
        # api.views, we should consolidate it at some point.
        for index, pair in enumerate(EDUCATION_CHOICES):
            if self.education_level == pair[0]:
                return [
                    # No idea why mypy suddenly doesn't like this but I
                    # don't have time to deal with it now.
                    ed[0] for ed in EDUCATION_CHOICES[index:]
                ]

        raise AssertionError('this should never be reached')

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        return qs.filter(
            min_years_experience__gte=self.min_years_experience,
            education_level__in=self.get_valid_education_levels()
        )

    def get_data_explorer_qs_params(self) -> QueryStringTuple:
        return (
            ('min_experience', str(self.min_years_experience)),
            ('education', ','.join(self.get_valid_education_levels())),
        )

    def get_exp_comparable_search_criteria(self) -> str:
        return "{} years or greater".format(self.min_years_experience)

    def get_edu_comparable_search_criteria(self) -> str:
        return ','.join(self.get_valid_education_levels())
