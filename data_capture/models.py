import hashlib
import logging

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.utils import timezone
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from contracts.models import (Contract, CashField, EDUCATION_CHOICES,
                              MIN_ESCALATION_RATE, MAX_ESCALATION_RATE)


logger = logging.getLogger('calc')


@deconstructible
class SlowpokeStorage(Storage):
    def _open(self, name, mode='rb'):
        obj = SlowpokeStorageModel.objects.filter(name=name).get()
        return ContentFile(obj.data)

    def _save(self, name, content):
        data = content.read()
        obj = SlowpokeStorageModel(name=name, data=data, size=len(data))
        obj.save()
        return name

    def exists(self, name):
        return SlowpokeStorageModel.objects.filter(name=name).exists()

    def size(self, name):
        return SlowpokeStorageModel.objects.filter(name=name).get().size


class SlowpokeStorageModel(models.Model):
    data = models.BinaryField()

    size = models.IntegerField()

    name = models.CharField(max_length=128, unique=True, db_index=True)


class HashedUploadedFile(models.Model):
    HASH_NAME = 'sha256'

    HASH_HEXDIGEST_LEN = 64

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    hex_hash = models.CharField(
        max_length=HASH_HEXDIGEST_LEN,
        db_index=True,
        unique=True
    )

    contents = models.FileField(
        upload_to='data_capture_uploaded_files/',
        storage=SlowpokeStorage()
    )

    @classmethod
    def get_hex_hash(cls, f):
        f.seek(0)
        hasher = getattr(hashlib, cls.HASH_NAME)()
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
        f.seek(0)
        return hasher.hexdigest()

    @classmethod
    def store(cls, f):
        hex_hash = cls.get_hex_hash(f)
        q = cls.objects.filter(hex_hash=hex_hash)
        if q.exists():
            return q.get()
        obj = cls(hex_hash=hex_hash, contents=f)
        obj.save()
        f.seek(0)
        return obj


class AttemptedPriceListSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    submitter = models.ForeignKey(User)

    uploaded_file = models.ForeignKey(HashedUploadedFile, null=True,
                                      blank=True)

    uploaded_file_name = models.CharField(max_length=128, blank=True)

    uploaded_file_content_type = models.CharField(max_length=128, blank=True)

    valid_row_count = models.IntegerField(null=True, blank=True)

    invalid_row_count = models.IntegerField(null=True, blank=True)

    session_state = JSONField()

    def set_uploaded_file(self, f):
        self.uploaded_file = HashedUploadedFile.store(f)
        self.uploaded_file_name = f.name
        self.uploaded_file_content_type = f.content_type

    def restore_uploaded_file(self):
        contents = self.uploaded_file.contents
        contents.open()
        return SimpleUploadedFile(
            name=self.uploaded_file_name,
            content=contents.read(),
            content_type=self.uploaded_file_content_type,
        )


class SubmittedPriceList(models.Model):
    CONTRACTOR_SITE_CHOICES = [
        ('Customer', 'Customer/Offsite'),
        ('Contractor', 'Contractor/Onsite'),
        ('Both', 'Both'),
    ]

    STATUS_UNREVIEWED = 0
    STATUS_APPROVED = 1
    STATUS_RETIRED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (
        (STATUS_UNREVIEWED, 'unreviewed'),
        (STATUS_APPROVED, 'approved'),
        (STATUS_RETIRED, 'retired'),
        (STATUS_REJECTED, 'rejected'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This is the equivalent of Contract.idv_piid.
    contract_number = models.CharField(
        max_length=128,
        help_text='List the full contract number, e.g. GSXXXXXXX or 47XXXXXXXXXXX.',
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9-_]+$',
            message='Please use only letters, numbers, and dashes (-).')],
    )
    vendor_name = models.CharField(max_length=128)
    schedule = models.CharField(
        max_length=128
    )
    is_small_business = models.BooleanField()
    contractor_site = models.CharField(
        verbose_name='Worksite',
        choices=CONTRACTOR_SITE_CHOICES,
        max_length=128
    )
    contract_start = models.DateField(
        null=True,
        blank=True,
    )
    contract_end = models.DateField(
        null=True,
        blank=True,
    )
    escalation_rate = models.FloatField(
        verbose_name='escalation rate (%)',
        validators=[MinValueValidator(MIN_ESCALATION_RATE),
                    MaxValueValidator(MAX_ESCALATION_RATE)]
    )

    submitter = models.ForeignKey(User)

    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS_UNREVIEWED)
    status_changed_by = models.ForeignKey(User, related_name='+')
    status_changed_at = models.DateTimeField()

    uploaded_filename = models.CharField(
        max_length=128,
        help_text=(
            'Name of the file that was uploaded, as it was called on '
            'the uploader\'s system. For display purposes only.'
        )
    )
    serialized_gleaned_data = models.TextField(
        help_text=(
            'The JSON-serialized data from the upload, including '
            'information about any rows that failed validation.'
        )
    )

    def add_row(self, **kwargs):
        row = SubmittedPriceListRow(**kwargs)
        row.price_list = self
        row.save()
        return row

    def get_schedule_title(self):
        # We're importing here to avoid a circular import. Kinda icky.
        from .schedules.registry import get_class

        return get_class(self.schedule).title

    def get_business_size_string(self):
        # 'S' means 'Small Business' and 'O' means 'Other'
        if self.is_small_business:
            return 'S'
        return 'O'

    def _change_status(self, status, user):
        self.status = status
        self.status_changed_at = timezone.now()
        self.status_changed_by = user

        status_name = self.STATUS_CHOICES[status][1]
        logger.info(f'Price list with id {self.id} has been set to '
                    f'{status_name} by user id {user.id} ({user.email})')

    def approve(self, user):
        '''
        Approve this SubmittedPriceList. This causes its rows of pricing data
        to be converted to Contract models, which are then accessible via
        CALC's API and in the Data Explorer.
        '''
        self._change_status(self.STATUS_APPROVED, user)

        for row in self.rows.filter(is_muted=False):
            if row.contract_model is not None:
                raise AssertionError()

            contract = Contract(
                idv_piid=self.contract_number,
                contract_start=self.contract_start,
                contract_end=self.contract_end,
                vendor_name=self.vendor_name,
                labor_category=row.labor_category,
                education_level=row.education_level,
                min_years_experience=row.min_years_experience,
                contractor_site=self.contractor_site,
                schedule=self.get_schedule_title(),
                business_size=self.get_business_size_string(),
                sin=row.sin,
                keywords=row.keywords,
                certifications=row.certifications,
                security_clearance=row.security_clearance,
            )

            contract.adjust_contract_year()

            # Assuming the rate in the price list is the 'base rate'
            # Escalate the hourly_rate_yearX fields
            contract.escalate_hourly_rate_fields(
                row.base_year_rate, self.escalation_rate)

            # Update current/next/second year price fields
            contract.update_price_fields()

            contract.full_clean(exclude=['piid'])
            contract.save()
            row.contract_model = contract
            row.save()

        self.save()

    def unreview(self, user):
        '''
        Mark this SubmittedPriceList as "unreviewed" and delete all associated
        Contract models. An "unreviewed" price list is one that has been
        either newly submitted or that has had modifications made to it and
        requires review (to approve or reject it) by an administrator.
        '''
        self._change_status(self.STATUS_UNREVIEWED, user)
        self._delete_associated_contracts()
        self.save()

    def retire(self, user):
        '''
        Mark this SubmittedPriceList as "retired" and delete all associated
        Contract models. Retiring a price list is for removing a once approved
        price list that is now either out-of-date or now otherwise invalid.
        '''
        self._change_status(self.STATUS_RETIRED, user)
        self._delete_associated_contracts()
        self.save()

    def reject(self, user):
        '''
        Reject this SubmittedPriceList. This method should be called on
        "unreviewed" price lists. It is the opposite of approving a price list.
        '''
        if self.status is not self.STATUS_UNREVIEWED:
            raise AssertionError()
        self._change_status(self.STATUS_REJECTED, user)
        self.save()

    def _delete_associated_contracts(self):
        for row in self.rows.all():
            if row.contract_model:
                row.contract_model.delete()
        self.save()

    def __str__(self):
        return "Price List for {}".format(self.contract_number)

    @classmethod
    def get_latest_by_contract_number(cls, contract_number):
        return cls.objects.filter(
            contract_number__iexact=contract_number).latest(
            'status_changed_at')


class SubmittedPriceListRow(models.Model):
    labor_category = models.TextField()
    education_level = models.CharField(
        choices=EDUCATION_CHOICES, max_length=5, null=True,
        blank=True)
    min_years_experience = models.IntegerField()
    base_year_rate = CashField(max_digits=10, decimal_places=2)
    sin = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    certifications = models.TextField(null=True, blank=True)
    security_clearance = models.TextField(null=True, blank=True)
    is_muted = models.BooleanField(
        help_text=(
            "Whether to include this row in CALC data once its "
            "price list has been approved"
        ),
        default=False
    )

    price_list = models.ForeignKey(
        SubmittedPriceList,
        on_delete=models.CASCADE,
        related_name='rows'
    )

    # If this row is represented in the Contract model objects, this will be
    # non-null. Note that we're explicitly calling it "contract model" here
    # because the Contract model isn't named very accurately: it doesn't
    # really represent a contract, but rather *part* of a contract, so
    # to avoid confusion, we're referring to it as the "contract model".
    contract_model = models.OneToOneField(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        # This is really just so price list rows don't appear as
        # 'SubmittedPriceListRow object' in Django admin.

        return 'Submitted price list row'


class capability_statement(models.Model):
    contract_number = models.CharField(max_length=50, null=False, blank=False)
    url = models.URLField(max_length=2500, null=False, blank=False)
