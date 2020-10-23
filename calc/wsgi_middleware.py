def static_url_rewriter(app, src_prefix, dest_prefix):
    '''
    WSGI middleware to rewrite the `PATH_INFO` of the WSGI
    environment based on a source and destination prefix.

    The content being served from the site is assumed to be static
    content, so `index.html` is appended to the path if needed.
    '''

    def wrapper(environ, start_response):
        path = environ['PATH_INFO']
        if path == src_prefix[:-1]:
            start_response('302 Found', [
                ('Location', src_prefix)
            ])
            return []
        elif path.startswith(src_prefix):
            path_info = dest_prefix + path[len(src_prefix):]
            if path_info.endswith('/'):
                path_info += 'index.html'
            environ['PATH_INFO'] = path_info
        return app(environ, start_response)

    return wrapper
