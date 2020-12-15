from . import safe_mode


def is_safe_mode_enabled(request):
    '''Include is_safe_mode_enabled in all request contexts'''

    return {'is_safe_mode_enabled': safe_mode.is_enabled(request)}
