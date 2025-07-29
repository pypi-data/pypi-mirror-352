# Copyright 2025 Cegal AS
# All rights reserved


import string


class DefaultPageHandler(object):
    """Used by default when no page_handler is specified"""

    def landing_page(self):
        """Returns the HTML that the user sees after authenticating, and instructs the server to stop serving further responses"""
        return (
            False,
            "<html><head><title>Keystone login</title></head><body><p>Keystone login successful. You can close this window</p></body></html>",
        )

    def get(self, parsed_url, access_token_factory):
        return (False, "")


class CegalProductTemplate:
    def __init__(self, **kwargs):
        self._params = {
            **{
                "product": "Unknown product",
                "version": None,
                "extra": "",
                "logo": _logo_data_uri,
            },
            **kwargs,
        }

    def landing_page(self):
        """Returns the HTML that the user sees after authenticating, and instructs the server to stop serving further responses"""

        if self._params["version"] is None:
            self._params["full_version_msg"] = ""
        else:
            self._params["full_version_msg"] = f"(version {self._params['version']})"

        src = string.Template(
            "<html><head><title>Keystone login</title></head><body><p><img width='20%' src=$logo alt='Cegal logo' /><hr/><h1>Keystone login successful. You can close this window.</h1><div>Login requested by $product $full_version_msg</div>$extra</body></html>"
        )

        return (False, src.substitute(self._params))

    def get(self, parsed_url, access_token_factory):
        return (False, "")


class TwoStagePageHandler:
    """An example of a two-stage landing page.  The initial landing_page refreshes itself."""

    def landing_page(self):
        """Returns the HTML that the user sees after authenticating, briefly, and redirects to the /landing page.  Instructs the server to continue serving further requests"""
        return (
            True,
            "<html><head><meta http-equiv='refresh' content='0; url=/landing'><title>Keystone login</title></head><body><p>Keystone login successful. This window will refresh to a second page automatically</p></body></html>",
        )

    def get(self, parsed_url, access_token_factory):
        """A minimal example of routing and serving the /landing page

        The access_token_factory is passed so that the page can *lazily* retrieve the access_token, which the client
        is simultaneously retrieving once the first page has communicated the auth_code.  The factory must be thread-safe.

        Note:  a full-fledged http and routing abstraction is overkill for our current use-cases, but
        it could easily evolve from this."""
        if parsed_url.path == "/landing":
            try:
                return (
                    False,
                    f"""
<html><body>
2nd page<hr>
Access token: {access_token_factory()}
</body></html>
""",
                )
            except Exception as e:
                return (
                    False,
                    f"""
<html><body>
Error<hr>
{e}
</body></html>
""",
                )
        else:
            # continue serving if another page (e.g. at least /favicon.ico!) is requested
            return (True, "")


# the cegal logo as a data URI so we don't have to serve extra assets
_logo_data_uri = r"data:image/png;base64,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"
