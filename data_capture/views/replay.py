from functools import wraps
from django.http import HttpResponseForbidden

from ..management.commands.initgroups import VIEW_ATTEMPT_PERMISSION
from ..models import AttemptedPriceListSubmission
from .common import get_nested_item


class Replayer:
    '''
    A class used for managing the recording and replaying of
    price list uploads.

    It's assumed that price list upload endpoints conform to
    the following:

      * Respond to a POST request with the 'file' parameter
        containing a price list file that has been uploaded.

      * Store all relevant price list-related data in a
        session key. The value of this session key should
        be a dict.
    '''

    def __init__(self, base_session_key):
        self.base_session_key = base_session_key

    def _get_replay_id(self, request):
        replay_id = get_nested_item(request.session, (
            self.base_session_key,
            'replay_id',
        ))
        if replay_id:
            replay_id = int(replay_id)
        return replay_id

    def context_processor(self, request):
        '''
        A context processor that adds information about the current
        AttemptedPriceListSubmission being replayed, if any.
        '''

        replay_id = self._get_replay_id(request)
        replay = None

        if replay_id:
            # Just in case the replay has disappeared since the user
            # started replaying, we'll use `first()` to get the attempt,
            # so that we don't crash if the replay no longer exists.
            replay = AttemptedPriceListSubmission.objects.filter(
                pk=replay_id).first()

        return {'replay': replay}

    def _load_replay(self, request):
        '''
        Load the replay specified by the given POST request.

        This essentially makes the request's session and POST
        data look like it did when the replay was originally
        recorded.
        '''

        attempt_id = request.POST['replay-attempted-submission']
        attempt = AttemptedPriceListSubmission.objects.filter(
            pk=int(attempt_id)).get()
        request.session[self.base_session_key] = {
            'replay_id': attempt_id,
            **attempt.session_state
        }
        if attempt.uploaded_file:
            request.FILES['file'] = attempt.restore_uploaded_file()

    @staticmethod
    def can_view_replays(user):
        '''
        Returns whether or not the given User has permission to
        view replays.
        '''

        return user.is_staff and user.has_perm(VIEW_ATTEMPT_PERMISSION)

    def recordable(self, func):
        '''
        A view decorator that makes a view recordable and replayable.

        The view will be passed 'recorder' as a keyword argument;
        it will be a Recorder instance that can be used to add
        additional metadata to the recording.
        '''

        @wraps(func)
        def view(request, *args, **kwargs):
            if (request.method == 'POST' and
                    'replay-attempted-submission' in request.POST):
                if not self.can_view_replays(request.user):
                    return HttpResponseForbidden()
                self._load_replay(request)

            with Recorder(self, request) as recorder:
                kwargs['recorder'] = recorder
                return func(request, *args, **kwargs)

        return view

    def is_replay(self, request):
        '''
        Returns whether the given request represents a replay.
        '''

        return bool(self._get_replay_id(request))


class Recorder:
    '''
    A class used for managing the recording of a price list
    upload request.

    It is passed to views with the Replayer.recordable decorator
    and can be used to attach additional metadata to a recording.

    Note that a Recorder instance may not actually represent an
    actual recording, because the same view function is called
    for both recordings and replays. If the view function is
    called in the context of a replay, the Recorder passed to
    it will be usable, but its method calls will largely be no-ops.
    '''

    def __init__(self, replayer, request):
        self.attempt = None

        if request.method == 'POST' and not replayer.is_replay(request):
            self.attempt = AttemptedPriceListSubmission(
                submitter=request.user,
                session_state=request.session[replayer.base_session_key]
            )
            if 'file' in request.FILES:
                self.attempt.set_uploaded_file(request.FILES['file'])
            self.attempt.valid_row_count = 0
            self.attempt.invalid_row_count = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.attempt:
            self.attempt.save()

    def on_gleaned_data(self, gleaned_data):
        '''
        Associate gleaned data with a price list upload request.
        '''

        if self.attempt:
            self.attempt.valid_row_count = len(gleaned_data.valid_rows)
            self.attempt.invalid_row_count = len(gleaned_data.invalid_rows)
