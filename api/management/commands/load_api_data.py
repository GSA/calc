import math
import requests
from tqdm import tqdm
from django.core.management import BaseCommand, CommandError

from contracts.models import Contract
from api.serializers import ContractSerializer


def iter_api_pages(url, start_page=1, end_page=None):
    page = start_page
    while True:
        if end_page is not None and page > end_page:
            break
        res = requests.get(f"{url}?page={page}").json()
        results = res['results']
        for result in results:
            del result['id']

        if len(results):
            max_page = math.ceil(res['count'] / len(results))
        else:
            max_page = page
        if end_page is not None:
            max_page = min(end_page, max_page)
        total_pages = max_page - start_page + 1

        yield results, total_pages

        if res['next'] is not None:
            page += 1
        else:
            break


class Command(BaseCommand):
    help = "Load rate data from the API of another CALC instance."

    DEFAULT_URL = "https://api.data.gov/gsa/calc/rates/"

    def add_arguments(self, parser):
        parser.add_argument(
            '-s', '--start-page',
            default=1,
            type=int,
            help='start page (default is 1)'
        )

        parser.add_argument(
            '-e', '--end-page',
            default=None,
            type=int,
            help='end page (default is to read all pages)'
        )

        parser.add_argument(
            '--append',
            default=False,
            action='store_true',
            help='append to existing rates (instead of deleting them first)'
        )

        parser.add_argument(
            '--dry-run',
            default=False,
            action='store_true',
            help='don\'t actually change the database'
        )

        parser.add_argument(
            '-u', '--url',
            default=self.DEFAULT_URL,
            help=f'URL of CALC API (default is {self.DEFAULT_URL})'
        )

    def process_pages(self, pages, dry_run):
        num_rates = 0
        num_pages = 0
        progress_bar = None

        try:
            for rates, total_pages in pages:
                if progress_bar is None:
                    progress_bar = tqdm(total=total_pages)
                serializer = ContractSerializer(data=rates, many=True)
                if serializer.is_valid():
                    num_rates += len(rates)
                    if not dry_run:
                        serializer.save()
                else:
                    rates_with_errors = [
                        (r, e) for r, e in zip(rates, serializer.errors)
                        if e
                    ]
                    for rate, error in rates_with_errors:
                        self.stderr.write(
                            f"Rate {self.style.WARNING(rate)} has "
                            f"error {self.style.ERROR(error)}!"
                        )
                progress_bar.update(1)
                num_pages += 1
        finally:
            if progress_bar is not None:
                progress_bar.close()

        return num_rates, num_pages

    def handle(self, *args, **options):
        url = options['url']
        start_page = options['start_page']
        end_page = options['end_page']
        dry_run = options['dry_run']

        if end_page is not None and start_page > end_page:
            raise CommandError('Start page cannot be greater than end page!')

        if not options['append'] and not dry_run:
            self.stdout.write("Deleting all existing rate information.")
            Contract.objects.all().delete()

        self.stdout.write(f"Loading new rate information from {url}.")

        pages = iter_api_pages(url, start_page, end_page)
        num_rates, num_pages = self.process_pages(pages, dry_run)

        if dry_run:
            self.stdout.write(
                f"Processed {num_rates} rates in dry run mode "
                f"over {num_pages} pages.")
        else:
            if num_rates == 0:
                self.stdout.write(self.style.WARNING(
                    f"No rates were written to the database."))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Done writing {num_rates} rates to the database."))
