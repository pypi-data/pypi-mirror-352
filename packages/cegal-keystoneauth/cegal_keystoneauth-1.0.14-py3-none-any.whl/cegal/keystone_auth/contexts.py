from cegal.keystone_auth.identityserver import IdentityServer


class ExternalKeystoneContext:
    _identity_server = IdentityServer()

    @property
    def identity_server(self):
        return self._identity_server

    def request_authcode_url(self, authorize_endpoint, params):
        from urllib.parse import urlencode

        params = urlencode(params)

        url = f"{authorize_endpoint}?{params}"

        import webbrowser

        wb = webbrowser.get()
        wb.open_new(url)
