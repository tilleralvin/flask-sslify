# -*- coding: utf-8 -*-

from flask import request, redirect

YEAR_IN_SECS = 31536000


class SSLify(object):
    """Secures your Flask App."""

    def __init__(self, app=None, age=YEAR_IN_SECS, subdomains=False, permanent=False):
        self.hsts_age = age
        self.hsts_include_subdomains = subdomains
        self.permanent = permanent

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Configures the configured Flask app to enforce SSL."""

        self.app = app
        app.before_request(self.redirect_to_ssl)
        app.after_request(self.set_hsts_header)

    @property
    def hsts_header(self):
        """Returns the proper HSTS policy."""
        hsts_policy = 'max-age={0}'.format(self.hsts_age)

        if self.hsts_include_subdomains:
            hsts_policy += '; includeSubDomains'

        return hsts_policy

    def redirect_to_ssl(self):
        """Redirect incoming requests to HTTPS."""
        # Should we redirect?

        # Use Flask config variable USE_SSL
        use_ssl = app.config.get('USE_SSL', None)
        if use_ssl is None:
            use_ssl = not (self.app.debug)

        criteria = [
            request.is_secure,
            not (use_ssl),
            request.headers.get('X-Forwarded-Proto', 'http') == 'https'
        ]

        if not any(criteria):
            if request.url.startswith('http://'):
                url = request.url.replace('http://', 'https://', 1)
                code = 302
                if self.permanent:
                    code = 301
                r = redirect(url, code=code)

                return r

    def set_hsts_header(self, response):
        """Adds HSTS header to each response."""
        if request.is_secure:
            response.headers.setdefault('Strict-Transport-Security', self.hsts_header)
        return response
