import bleach
import csv
from datetime import datetime
from decimal import Decimal

from django.db import models, connection
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.utils.html import strip_tags

from calc.utils import markdown_to_sanitized_html

EDUCATION_CHOICES = (
    ('HS', 'High School'),
    ('AA', 'Associates'),
    ('BA', 'Bachelors'),
    ('MA', 'Masters'),
    ('PHD', 'Ph.D.'),
)

MIN_ESCALATION_RATE = 0
MAX_ESCALATION_RATE = 99
NUM_CONTRACT_YEARS = 5


def clean_search(query):
    '''
    Takes a query input, sanitizes it, and finds synoymns.

    If there are multiple search terms (comma-delimited)
    it will parse the string into an array of strings.

    We're using the CSV module rather than a simple split()
    so quoted sub-strings (like "engineer, junior") will be kept together,
    allowing for commas in sub-strings.

    Note that after normalization, all terms will be lower-case and
    abbreviated synonyms are changed to the long version.

    Examples:

        >>> clean_search('Lone Ranger')
        ['lone ranger']

        >>> clean_search('jane,jim,Jacky,joe')
        ['jane', 'jim', 'jacky', 'joe']

        >>> clean_search('carrot, beet  , Sunchoke')
        ['carrot', 'beet', 'sunchoke']

        >>> clean_search('turkey, "Hog, wild", cow')
        ['turkey', 'hog, wild', 'cow']

        >>> clean_search("an <script>EVIL()</script> example")
        ['an evil() example']

        >>> clean_search('sr. frog, sme, disco chicken')
        ['senior frog', 'subject matter expert', 'disco chicken']
    '''
    # First, let's clean the query and not allow any tags in there.
    stripped = strip_tags(query)
    clean_query = bleach.clean(stripped, tags=[], strip=True)
    # Then extract the terms to a list
    if ',' in clean_query:
        reader = csv.reader([clean_query], skipinitialspace=True)
        terms = [qq.strip() for qq in list(reader)[0] if qq.strip()]
    else:
        terms = [clean_query]
    # Finally, normalize and look for synonyms
    terms = [Contract.normalize_labor_category(t) for t in terms]
    return terms


class CurrentContractManager(models.Manager):
    def bulk_update_normalized_labor_categories(self):
        '''
        Iterate through all Contract models and update their
        normalized labor categories if necessary.

        This method does not trigger any pre/post save signals or
        call Contract.save().
        '''

        pks = []
        updates = []
        num_updates = 0
        for contract in self.only('id', 'labor_category', '_normalized_labor_category'):
            if contract.update_normalized_labor_category():
                pks.append(contract.id)
                updates.append(contract.id)
                updates.append(contract._normalized_labor_category)
                num_updates += 1
        if updates:
            print("Updating {} rows.".format(num_updates))
            with connection.cursor() as cursor:
                values = []
                for i in range(num_updates):
                    values.append(r'(%s, %s)')
                values_str = ", ".join(values)
                sql = (  # nosec
                    "UPDATE contracts_contract "
                    "  SET _normalized_labor_category = v.nlc"
                    "  FROM (VALUES" + values_str + ") AS v (id, nlc)"
                    "  WHERE contracts_contract.id = v.id"
                )
                cursor.execute(sql, updates)
            self.filter(pk__in=pks).update_search_index()
        return num_updates

    def bulk_create(self, contracts, *args, **kwargs):
        for contract in contracts:
            contract.update_normalized_labor_category()
        contracts = super().bulk_create(contracts, *args, **kwargs)
        self.filter(pk__in=[c.pk for c in contracts]).update_search_index()
        return contracts

    def search(self, *args, **kwargs):
        return self.get_queryset().search(*args, **kwargs)

    def get_queryset(self):
        return ContractsQuerySet(self.model, using=self._db)\
            .filter(current_price__gt=0)\
            .exclude(current_price__isnull=True)


class ContractsQuerySet(models.QuerySet):

    def search(self, query):
        return self.filter(search_index=query)

    def update_search_index(self):
        return self.update(
            search_index=SearchVector('_normalized_labor_category'))

    def order_by(self, *args, **kwargs):
        edu_sort_sql = """
            case
                when education_level = 'HS' then 1
                when education_level = 'AA' then 2
                when education_level = 'BA' then 3
                when education_level = 'MA' then 4
                when education_level = 'PHD' then 5
                else -1
            end
        """

        edu_index = None

        sort_params = list(args)

        if 'education_level' in sort_params:
            edu_index = sort_params.index('education_level')
        elif '-education_level' in sort_params:
            edu_index = sort_params.index('-education_level')

        if edu_index is not None:
            sort_params[edu_index] = 'edu_sort' if not args[
                edu_index].startswith('-') else '-edu_sort'
            queryset = super(ContractsQuerySet, self)\
                .extra(select={'edu_sort': edu_sort_sql}, order_by=sort_params)
        else:
            queryset = super(ContractsQuerySet, self)\
                .order_by(*args, **kwargs)

        return queryset

    def multi_phrase_search(self, query, query_by=None, *args, **kwargs):
        """
        Given a query as string, runs it through clean_search to get a list of search terms,
        then returns a matching queryset of Contract objects for each of those terms.

        Optional arguments:
            'match_exact' only returns exact matches.
            'match_any' matches any word, so "business manager" will also match "dev manager"
            'query_by' specifies fields other than labor_category you may wish to search for.
        """
        matches = Contract.objects.none()
        qs = self.get_queryset()
        phrases = clean_search(query)
        if not query_by:
            query_by = '_normalized_labor_category'
        if 'match_exact' in args:
            # This will match each phrase they enter exactly.
            # We use an or operator here to build up the total queryset from
            # each exactly matched item they found.
            for phrase in phrases:
                filter_by = {query_by + '__iexact': phrase}
                matches = matches | qs.filter(**filter_by)
        elif query_by != '_normalized_labor_category':
            for phrase in phrases:
                filter_by = {query_by + '__icontains': phrase}
                matches = matches | qs.filter(**filter_by)
        else:
            # Match any: Break phrases down into individual words
            # So "business manager" finds results with "business" AND "manager"
            # anywhere in the labor category.
            # Note this is relatively hard on the DB, producing one query per word,
            # but given our number of users, small queries and indexing, we should be OK.

            for phrase in phrases:
                # If the phrase is quoted, we want to use it as
                if phrase.startswith("'") or phrase.startswith('"'):
                    filter_by = {query_by + '__icontains': phrase}
                    matches = matches | qs.filter(**filter_by)
                else:
                    # Break out the individual words. Here, we only want results with AND matching.
                    # So 'business analyst' will only return phrases matching both words.
                    words = phrase.split(' ')
                    # We need a starter queryset for the intersection
                    wmatches = qs.filter(_normalized_labor_category__icontains=words[0])
                    for w in words:
                        filter_by = {query_by + '__icontains': w}
                        wmatches = wmatches & qs.filter(**filter_by)
                    # Now add the word matches onto the overall matches as an OR
                    matches = matches | wmatches
        return matches

    def get_queryset(self):
        return ContractsQuerySet(self.model, using=self._db)\
            .filter(current_price__gt=0)\
            .exclude(current_price__isnull=True)


class BulkUploadContractSource(models.Model):
    '''
    Model to store provenance of bulk-uploaded contract data
    '''
    REGION_10 = 'R10'
    SCHEDULE_70 = 'S70'

    PROCUREMENT_CENTER_CHOICES = (
        (REGION_10, 'Region 10'),
        (SCHEDULE_70, 'Schedule 70'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitter = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    has_been_loaded = models.BooleanField(default=False)
    original_file = models.BinaryField()
    file_mime_type = models.TextField()
    procurement_center = models.CharField(
        db_index=True, max_length=5, choices=PROCUREMENT_CENTER_CHOICES)


class CashField(models.DecimalField):
    '''
    Custom field class for storing cash amounts in U.S. dollars and cents.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.decimal_places != 2:
            raise ValueError(f'{self.__class__.__name__} must have '
                             f'exactly 2 decimal places')

    @staticmethod
    def cash(val):
        '''
        Converts the given value, which may be a floating-point number,
        to a Decimal that represents a monetary value.

        Examples:

            >>> CashField.cash(1.0 / 3)
            Decimal('0.33')

            >>> CashField.cash(350)
            Decimal('350.00')
        '''

        return Decimal(val).quantize(Decimal('.01'))

    def to_python(self, value):
        '''
        It's possible that our cash-related fields have been set to
        float values that don't convert nicely to Decimal values with
        a reasonable number of digits in the cents part.

        This will trip Django 1.9's max_digits validators, so we'll
        ensure that our values don't have an excessive number of cents
        digits.
        '''

        value = super().to_python(value)
        if value is None:
            return value
        return self.cash(value)


class Contract(models.Model):
    '''
    The name of this model, "Contract", is a bit of a misnomer: in
    reality it reflects an individual labor category of a
    contract.

    This model stores denormalized data about labor category
    pricing in federal contracts. It is denormalized because
    rather than having a separate model containing
    general metadata about an individual contract (such as
    a vendor name) and storing a foreign key in this model
    that points to it, we store all such information
    directly in this model. This means that such information
    is duplicated across all model instances that correspond
    to different labor categories in the same contract.
    '''

    # This field stores the contract number, but has an
    # unusual name, which we think comes from:
    #
    #   IDV - "Indefinite Delivery Vehicle"
    #   PIID - "Procurement Instrument Identification"

    idv_piid = models.CharField(
        max_length=128, db_index=True,
        verbose_name="contract number")  # index this field
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    contract_year = models.IntegerField(null=True, blank=True)
    vendor_name = models.CharField(max_length=128, db_index=True)
    labor_category = models.TextField(db_index=True)
    education_level = models.CharField(
        db_index=True, choices=EDUCATION_CHOICES, max_length=5, null=True,
        blank=True)
    min_years_experience = models.IntegerField(db_index=True)
    hourly_rate_year1 = CashField(max_digits=10, decimal_places=2)
    hourly_rate_year2 = CashField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year3 = CashField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year4 = CashField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate_year5 = CashField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    current_price = CashField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    next_year_price = CashField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    second_year_price = CashField(
        db_index=True, max_digits=10, decimal_places=2, null=True, blank=True)
    contractor_site = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    schedule = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    business_size = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    keywords = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    certifications = models.CharField(
        db_index=True, max_length=128, null=True, blank=True)
    description = models.CharField(
        db_index=True, max_length=1000, null=True, blank=True
    )
    security_clearance = models.CharField(
        db_index=True, max_length=1000, null=True, blank=True
    )

    # SIN stands for "Special Item Number" and is is a categorization method
    # that groups similar products, services, and solutions together.
    #
    # Unfortunately, this field isn't very useful because a labor category
    # can actually apply to multiple SIN numbers, and in practice this
    # field contains difficult-to-parse values like "874-1,2" and
    # "874-1 thru 7". For more details, see:
    #
    #   https://github.com/18F/calc/issues/1033
    sin = models.TextField(null=True, blank=True)

    _normalized_labor_category = models.TextField(db_index=True, blank=True)

    search_index = SearchVectorField(default='', db_index=True, editable=False)

    upload_source = models.ForeignKey(
        BulkUploadContractSource,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    # Ojects should be current contracts with a valid current_price
    objects = CurrentContractManager()

    @staticmethod
    def normalize_labor_category(val):
        '''
        Utility to normalize the given labor category by applying various
        synonyms and such to it. This allows, for example, searches for
        "senior engineer" to include labor categories like
        "sr. engineer".

        Note that this would ideally be done by modifying postgres'
        dictionary configuration, but at the time of this writing,
        that is untenable. For more details, see:

            https://github.com/18F/calc/issues/1375

        TO-DO: move this out so it's not cluttering up the model.
        This will require sorting out the
        `test_bulk_update_normalized_labor_categories_works` test
        that calls it, and probably simplifying the bulk_upload method.
        '''

        # Note also that any logic changes to this code should
        # eventually be followed-up with
        # `manage.py update_search_field`. Otherwise,
        # all pre-existing contracts will still have search
        # index information corresponding to the old logic.

        synonyms = {
            'jr': 'junior',
            'sr': 'senior',
            'sme': 'subject matter expert',
        }

        val = val.lower().replace('.', ' ')

        val = ' '.join([
            synonyms.get(word, word)
            for word in val.split()
        ])

        return val

    def get_readable_business_size(self):
        """
        There appears to be a mismatch between how we store business size
        in the DB and how we collect it in form submissions that makes startswith
        a safer check than equivalency
        """
        if self.business_size.lower().startswith('s'):
            return 'small business'
        else:  # We expect it should be 'o' but are not locking it down.
            return 'other than small business'

    @staticmethod
    def get_education_code(text, raise_exception=False):
        '''
        Given a human-readable education level, return its
        education code, e.g.:

            >>> Contract.get_education_code('High School')
            'HS'

        Return None if no education code matches the given
        text, unless raise_exception is True, in which
        case a ValueError is raised.
        '''

        for pair in EDUCATION_CHOICES:
            if text.strip() in pair[1]:
                return pair[0]

        if raise_exception:
            raise ValueError(text)
        return None

    @staticmethod
    def normalize_rate(rate):
        return float(rate.replace(',', '').replace('$', ''))

    def update_price_fields(self):
        '''
        Set current, next, and second year price fields based on this
        contract's contract_year.
        '''
        if self.contract_year is None:
            raise ValueError('self.contract_year must be set')

        curr_contract_year = self.contract_year

        contract_end_year = self.calculate_end_year()

        if 0 < curr_contract_year <= contract_end_year:
            self.current_price = self.get_hourly_rate(curr_contract_year)
        else:
            self.current_price = None

        if -1 < curr_contract_year < contract_end_year:
            self.next_year_price = self.get_hourly_rate(curr_contract_year + 1)
        else:
            self.next_year_price = None

        if -2 < curr_contract_year < contract_end_year - 1:
            self.second_year_price = self.get_hourly_rate(
                curr_contract_year + 2)
        else:
            self.second_year_price = None

    def escalate_hourly_rate_fields(self, base_year_rate, escalation_rate):
        if (escalation_rate < MIN_ESCALATION_RATE or
                escalation_rate > MAX_ESCALATION_RATE):
                raise ValueError(
                    'escalation_rate must be between {} and {}'.format(
                        MIN_ESCALATION_RATE, MAX_ESCALATION_RATE))

        self.hourly_rate_year1 = base_year_rate

        for i in range(2, NUM_CONTRACT_YEARS + 1):
            # use base rate by default
            next_rate = base_year_rate

            # if there is an escalation rate, increase the
            # previous year's value by the escalation rate
            if escalation_rate > 0:
                escalation_factor = Decimal(1 + escalation_rate / 100)
                prev_rate = self.get_hourly_rate(i - 1)
                next_rate = escalation_factor * prev_rate

            self.set_hourly_rate(i, next_rate)

    def adjust_contract_year(self, current_date=None):
        if current_date is None:
            current_date = datetime.today().date()

        if not self.contract_start:
            # TODO: What should happen in this case? Could also early return
            raise ValueError('contract_start must be defined')

        # Calculate the difference in years between the current_date and
        # the contract start date
        # (365.25 is used to account for leap years)
        curr_contract_year = int(
            (current_date - self.contract_start).days / 365.25) + 1

        self.contract_year = curr_contract_year

    def calculate_end_year(self):
        if not self.contract_start or not self.contract_end:
            raise ValueError('contract_start and contract_end must be defined')

        if self.contract_start > self.contract_end:
            raise ValueError('contract_start cannot be after contract_end')

        # Calculate the end year of the contract, with a ceiling of 5 (since
        # the hourly_rate_yearX fields only go up to 5)
        # (365.25 is used to account for leap years)
        contract_end_year = min(5, int(
            (self.contract_end - self.contract_start).days / 365.25) + 1)

        return contract_end_year

    def get_hourly_rate(self, year):
        if year < 1 or year > NUM_CONTRACT_YEARS:
            raise ValueError(
                'year must be in range 1 to {}'.format(NUM_CONTRACT_YEARS))
        return getattr(self, 'hourly_rate_year{}'.format(year))

    def set_hourly_rate(self, year, val):
        if year < 1 or year > NUM_CONTRACT_YEARS:
            raise ValueError(
                'year must be in range 1 to {}'.format(NUM_CONTRACT_YEARS))
        setattr(self, 'hourly_rate_year{}'.format(year), val)

    def update_normalized_labor_category(self):
        val = self.normalize_labor_category(self.labor_category)
        if self._normalized_labor_category != val:
            self._normalized_labor_category = val
            return True
        return False

    def save(self, *args, **kwargs):
        self.update_normalized_labor_category()
        super().save(*args, **kwargs)


class ScheduleMetadata(models.Model):
    '''
    This model represents metadata about a schedule, containing details
    such as the schedule's SIN number and description.
    '''

    class Meta:
        ordering = ['sin', 'name']

    # This column corresponds to the "schedule" column of the Contract model
    # and can essentially be viewed as an optional foreign key.
    schedule = models.CharField(
        help_text=(
            'Text that appears in the "schedule" column of Contract data '
            'to identify a labor rate as being in this schedule (e.g. "MOBIS").'
        ),
        unique=True,
        db_index=True,
        max_length=128
    )

    sin = models.CharField(
        help_text=(
            'The SIN number for the schedule (e.g. "874").'
        ),
        blank=True,
        max_length=128
    )

    name = models.CharField(
        help_text=(
            'The name of the schedule as it should appear to CALC users '
            '(e.g. "Legacy MOBIS").'
        ),
        max_length=128
    )

    description = models.TextField(
        help_text=(
            'A description of the schedule, formatted as Markdown.'
        ),
    )

    @property
    def full_name(self):
        return self.name

    @property
    def description_html(self):
        return markdown_to_sanitized_html(self.description)

    def __str__(self):
        return self.full_name
