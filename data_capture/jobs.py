import logging
import traceback
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django_rq import job

from . import email
from .r10_spreadsheet_converter import Region10SpreadsheetConverter
from contracts.loaders.region_10 import Region10Loader
from contracts.models import Contract, BulkUploadContractSource


contracts_logger = logging.getLogger('contracts')


def _create_contract_batches(upload_source, batch_size=5000, rows=None):
    if rows is None:
        r10_file = ContentFile(upload_source.original_file)
        converter = Region10SpreadsheetConverter(r10_file)
        rows = converter.convert_next()

    contracts = []
    bad_rows = []
    i = 0

    for row in rows:
        try:
            c = Region10Loader.make_contract(row, upload_source=upload_source)
            contracts.append(c)
        except (ValueError, ValidationError) as e:
            bad_rows.append(row)
        i += 1
        if i == batch_size:
            yield contracts, bad_rows
            i = 0
            contracts = []
            bad_rows = []

    if i > 0:
        yield contracts, bad_rows


@transaction.atomic
def _process_bulk_upload(upload_source):

    contracts_logger.info("Deleting contract objects related to region 10.")

    # Delete existing contracts identified by the same
    # procurement_center
    Contract.objects.filter(
        upload_source__procurement_center=BulkUploadContractSource.REGION_10
    ).delete()

    contracts_logger.info("Generating new contract objects.")

    total_contracts = 0
    total_bad_rows = 0

    for contracts, bad_rows in _create_contract_batches(upload_source):
        Contract.objects.bulk_create(contracts)
        total_contracts += len(contracts)
        total_bad_rows += len(bad_rows)
        contracts_logger.info(
            f"Saved {total_contracts} contracts so far "
            f"({total_bad_rows} bad rows found)."
        )

    # Update the upload_source
    upload_source.has_been_loaded = True
    upload_source.save()

    return total_contracts, total_bad_rows


@job
def process_bulk_upload_and_send_email(upload_source_id):
    contracts_logger.info(
        "Starting bulk upload processing (pk=%d)." % upload_source_id
    )
    upload_source = BulkUploadContractSource.objects.get(
        pk=upload_source_id
    )

    try:
        num_contracts, num_bad_rows = _process_bulk_upload(upload_source)
        email.bulk_upload_succeeded(upload_source, num_contracts, num_bad_rows)
    except Exception:
        contracts_logger.exception(
            'An exception occurred during bulk upload processing '
            '(pk=%d).' % upload_source_id
        )
        tb = traceback.format_exc()
        email.bulk_upload_failed(upload_source, tb)

    contracts_logger.info(
        "Ending bulk upload processing (pk=%d)." % upload_source_id
    )
