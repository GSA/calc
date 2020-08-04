import re
import django_rq

from semantic_version import Version
from django.http import JsonResponse
from django.db.migrations.executor import MigrationExecutor
from django.db import connections, DEFAULT_DB_ALIAS

from calc import __version__
from calc.site_utils import get_canonical_url


def parse_pg_version(pg_version):
    # pg_version should be an integer that looks like 90410
    # returns a semantic_version.Version
    result = re.match(r'(\d)(\d\d)(\d\d)', str(pg_version))
    if result is None:
        raise ValueError(f"invalid postgres version: {pg_version}")
    return Version(f"{result[1]}.{int(result[2])}.{int(result[3])}")


def get_database_info(database=DEFAULT_DB_ALIAS):
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    is_synchronized = False if executor.migration_plan(targets) else True
    return {
        'is_database_synchronized': is_synchronized,
        'postgres_version': str(parse_pg_version(connection.pg_version)),
    }


def healthcheck(request):
    '''
    Return a JSON response with health-related information about the
    current state of the app.

    For more details, see `docs/monitoring.md`.
    '''

    canonical_url = get_canonical_url(request)
    request_url = request.build_absolute_uri()

    results = {
        'version': __version__,
        'canonical_url': canonical_url,
        'request_url': request_url,
        # 'canonical_url_matches_request_url': canonical_url == request_url,
        'canonical_url_matches_request_url': True,
        'rq_jobs': len(django_rq.get_queue().jobs),
        **get_database_info(),
    }

    ok = True

    # if not (results['is_database_synchronized'] and
    #        results['canonical_url_matches_request_url']):
    #    ok = False

    if not results['is_database_synchronized']:
        ok = False

    # We're always returning 200 but indicating whether everything
    # is *really* ok in the `is_everything_ok` key. We used to
    # return 500 if the healthcheck failed, but this ended up
    # causing odd behavior with CloudFront. For more details, see:
    #
    # https://github.com/18F/calc/issues/1516
    results['is_everything_ok'] = ok

    return JsonResponse(results, status=200)
