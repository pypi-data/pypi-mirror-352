# Copyright 2025 Cegal AS
# All rights reserved

import base64
import json
import webbrowser
import threading
from secrets import token_urlsafe

import jwt
import os
import requests
from cegal.keystone_auth import logger, verify_tls
from cegal.keystone_auth.authorize import _AuthorizationClient
from cegal.keystone_auth.cache import _TokenCache
from cegal.keystone_auth.crypto import verify_access_token
from cegal.keystone_auth.device import _DeviceClient
from cegal.keystone_auth.nonce import _Nonce
from cegal.keystone_auth.options import OidcFlow
from cegal.keystone_auth.provider import Provider


class _TokenClient:
    def __init__(self, oidc_options, page_handler, context) -> None:
        self._context = context
        self.oidc_flow = oidc_options.oidc_flow
        self.client_id = oidc_options.client_id
        self.issuer = oidc_options.provider_uri
        self.provider_info = Provider(oidc_options.provider_uri, context)
        self.extra_scopes = (
            None
            if oidc_options.extra_scopes is None
            else " ".join(oidc_options.extra_scopes)
        )
        self.audience = oidc_options.audience
        self.local_storage = oidc_options.local_storage
        self.no_cache = oidc_options.no_cache
        self._token_cache = None
        self.page_handler = page_handler
        self._lock = threading.Lock()
        self._token_failed = False

    @property
    def access_token(self):
        if self._token_cache is None:
            self._token_cache = _TokenCache(
                self.local_storage, self.client_id, self.no_cache
            )
        # ensure thread-safety as multi-page landing pages might try to
        # retrieve the access_token during the auth procedure
        if self._token_failed:
            raise Exception(
                "Cannot retrieve access token due to earlier failure"
            )  # TODO better message
        self._lock.acquire()
        logger.debug("Getting access token for client_id %s", self.client_id)
        try:
            if (
                self._token_cache.refresh_token is not None
                and self._token_cache.id_token is not None
            ):
                logger.debug("Refresh token found in cache")
                return self._get_access_token()
            else:
                logger.debug("No refresh token found in cache, starting login flow")
                if (
                    self.oidc_flow == OidcFlow.auth_code
                    or self.oidc_flow == OidcFlow.auth_code_no_fallback
                ):
                    logger.debug("Using auth code flow")
                    self._login_interactive()
                elif self.oidc_flow == OidcFlow.device_code:
                    logger.debug("Using device code flow")
                    self._login_device()

                return self._get_access_token()
        except Exception:
            self._token_failed = True
            raise
        finally:
            self._lock.release()

    def _login_device(self):
        device_client = _DeviceClient(
            client_id=self.client_id,
            extra_scopes=self.extra_scopes,
            audience=self.audience,
            token_endpoint=self.provider_info.token_endpoint,
            device_authorization_endpoint=self.provider_info.device_authorization_endpoint,
            context=self._context,
        )
        data = device_client.get_token_with_device_flow()
        self._validate(data, False)

    def _login_interactive(self):
        auth_code, code_verifier, listener_address = self._login_user()
        # request token if there are return values, None could mean that device flow was initiated
        if auth_code and code_verifier and listener_address:
            self._request_token_from_endpoint(
                auth_code, code_verifier, listener_address
            )

    def delete_tokens(self):
        """
        Delete in memory and on disk tokens for the client.
        """
        logger.debug(
            "Destroying in-memory and on-disk tokens for client_id %s", self.client_id
        )
        if self._token_cache is None:
            return
        self._token_cache.delete_tokens()

    def delete_access_token(self):
        """
        Delete the on-disk and in-memory access token while keeping the refresh token
        """
        if self._token_cache is None:
            return
        logger.debug("Deleting access token for client id: %s", self.client_id)
        self._token_cache.delete_access_token()

    def _get_access_token(self):
        try:
            # Check if token is expired - if so, renew it
            # Note: We do not want to use leeway here as we want to renew the token if it's expired (no slack)
            # We previously used leeway but this caused a bug where the token was not renewed (due to leeway) and then passed to hub
            # Hub however did not accept the token as it was expired
            logger.debug("Checking if access token is valid")
            jwt.decode(
                self._token_cache.access_token,
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": True,
                },
            )
            logger.debug("Access token is valid")
            return self._token_cache.access_token
        except Exception:
            logger.info(
                "Failed to jwt.decode access token from cache. Renewing access token."
            )
            self._renew_access_token()
            return self._token_cache.access_token

    def _login_user(self):
        logger.debug("Logging in user")
        # Check env var for forcing device flow
        device_flow_env_var = os.environ.get(
            "CEGAL_KEYSTONE_AUTH_DEVICE_FLOW", default="false"
        ).lower()
        # ClientOption flag overrides env var
        if (
            device_flow_env_var == "true"
            and self.oidc_flow != OidcFlow.auth_code_no_fallback
        ):
            logger.debug(
                "Using device flow due to CEGAL_KEYSTONE_AUTH_DEVICE_FLOW env variable set"
            )
            self._login_device()
            return None, None, None

        if self.oidc_flow == OidcFlow.device_code:
            logger.debug("Using device flow due to OIDC flow set to 'device_code'")
            self._login_device()
            return None, None, None

        request_scopes = "openid"
        if self.extra_scopes is not None:
            request_scopes = request_scopes + " " + self.extra_scopes
        self.nonce = _Nonce()
        self.auth_client = _AuthorizationClient(self.page_handler, self, self._context)
        try:
            logger.debug("Attempting to authorize using auth code flow.")
            (
                auth_code,
                code_verifier,
                listener_address,
                self.nonce,
            ) = self.auth_client.authorize(
                self.client_id,
                request_scopes,
                self.provider_info.authorization_endpoint,
            )
        except webbrowser.Error as e:
            logger.debug("Webbrowser failed: %s", str(e))
            if self.oidc_flow == OidcFlow.auth_code_no_fallback:
                logger.warning(
                    "There was a browser control error and no fallback is configured."
                )
                raise webbrowser.Error(str(e))
            else:
                logger.debug("Webbrowser failed, falling back to device flow.")
                self._login_device()
                return None, None, None
        finally:
            self.auth_client.stop_listener()

        logger.debug("auth_code: " + auth_code)
        logger.debug("code_verifier: " + code_verifier)
        logger.debug("listener_address: " + listener_address)

        if (
            auth_code is not None
            and code_verifier is not None
            and listener_address is not None
        ):
            self.logged_in = True
        else:
            raise Exception("Not logged in")

        return auth_code, code_verifier, listener_address

    def _login_client_creds(self):
        logger.error("Client credentials are not supported yet")

    def _request_token_from_endpoint(self, auth_code, code_verifier, listener_address):
        resp = self._context.identity_server.request_token_from_endpoint(
            self.provider_info.token_endpoint,
            self.client_id,
            auth_code,
            code_verifier,
            listener_address,
            verify_tls,
        )
        data = json.loads(resp.content)
        self._validate(data)

    def _validate(self, data, validate_nonce=True):
        access_token = data["access_token"]
        id_token = data["id_token"]
        refresh_token = data["refresh_token"] if "refresh_token" in data else None
        self._validate_id_token(id_token, validate_nonce)
        self._validate_token_response(access_token, refresh_token, id_token)

    def _validate_token_response(self, access_token, refresh_token, id_token):
        verify_access_token(
            access_token,
            self.issuer,
            self.provider_info.jwks_uri,
            self._context,
            self.audience,
        )
        self._token_cache.access_token = access_token
        self._token_cache.refresh_token = refresh_token

        # Ensure token is stored regardless of if it a first-time or renewed token.
        self._token_cache.store_token(id_token, access_token, refresh_token)

    def _validate_id_token(self, id_token, validate_nonce=True):
        if len(id_token.split(".")) != 3:
            raise Exception("Invalid ID Token")

        try:
            payload = base64.b64decode(id_token.split(".")[1]).decode("utf-8")
            values = json.loads(payload)
        except:
            payload = base64.b64decode(id_token.split(".")[1] + "===").decode("utf-8")
            values = json.loads(payload)

        if validate_nonce:
            # If nonce has expired then we need to sign in again
            if self.nonce.has_expired():
                logger.warning("Nonce has expired.")
                self._login_user()

            if values["nonce"] != self.nonce.nonce:
                raise Exception("Nonce does not match")
            # Nonce has been verified and should now be deleted
            self.nonce = None

        self._token_cache.id_token = id_token

    def _renew_access_token(self):
        logger.info("Attempting to renew access token..")
        # Ref BUG66366 Programmatic access initializes auth flow
        # We have seen different token caches when reaching this from different instances of PKA, but there might be new tokens in DB.
        # Load tokens from DB and verify, if they are valid we do not need to start a new keystone request.
        if self._token_cache._load_token_from_db_and_verify():
            return
        request_body = {
            "grant_type": "refresh_token",
            "refresh_token": self._token_cache.refresh_token,
            "client_id": self.client_id,
            "client_secret": token_urlsafe(8),
        }

        resp = requests.post(
            self.provider_info.token_endpoint, data=request_body, verify=verify_tls
        )
        logger.debug("Response status code: %s", resp.status_code)
        if resp.status_code == 200:
            logger.debug("Token renewal successful")
            data = json.loads(resp.content)
            access_token = data["access_token"]
            id_token = data["id_token"]
            refresh_token = data["refresh_token"] if "refresh_token" in data else None

            self._validate_token_response(access_token, refresh_token, id_token)
        else:
            logger.info(
                "Renewal using refresh token failed. Refresh token likely expired. Re-starting login flow."
            )
            logger.info("Using OIDC flow: %s", self.oidc_flow)
            auth_code, code_verifier, listener_address = self._login_user()
            # self._login_user returns None if device flow was initiated
            # if there are return values we use auth code and need to request token
            if (
                auth_code is not None
                and code_verifier is not None
                and listener_address is not None
            ):
                self._request_token_from_endpoint(
                    auth_code, code_verifier, listener_address
                )
