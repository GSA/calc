from mimetypes import MimeTypes
from django.core.management import BaseCommand

from data_capture import jobs
from contracts.models import BulkUploadContractSource


class Command(BaseCommand):
    help = '''
    Bulk upload the given XLSX file.
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            help='input filename (.xlsx)'
        )

    def handle(self, *args, **options):
        filename = options['filename']

        f = open(filename, 'rb')
        upload_source = BulkUploadContractSource.objects.create(
            has_been_loaded=False,
            original_file=f.read(),
            file_mime_type=MimeTypes().guess_type(filename)[0],
            procurement_center=BulkUploadContractSource.REGION_10
        )
        f.close()

        ok, fails = jobs._process_bulk_upload(upload_source)

        self.stdout.write(
            f"{ok} contracts successfully processed, {fails} failed.\n"
        )
