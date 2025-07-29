# Copyright 2025 Cegal AS
# All rights reserved

import jwt
from cegal.keystone_auth import logger as logger
from cegal.keystone_auth.db import _TokenDb


class _TokenCache:
    _id_token = None
    _access_token = None
    _refresh_token = None

    def __init__(self, local_storage, client_id, no_cache) -> object:
        self._local_storage = local_storage
        self._client_id = client_id
        self._no_cache = no_cache
        if self._no_cache == False:
            logger.debug("Looking for token in local disk cache")
            self._db = _TokenDb(self._local_storage, client_id)
            self._load_token_from_db()
        else:
            logger.debug("Storing of tokens to disk is disabled")

    def _load_token_from_db(self):
        tokens = self._db.get_token_from_db()
        if tokens:
            self.id_token = tokens[1]
            self.access_token = tokens[2]
            self.refresh_token = tokens[3]

    def _load_token_from_db_and_verify(self) -> bool:
        try:
            self._load_token_from_db()
            logger.debug("Checking if access token is valid")
            jwt.decode(
                self.access_token,
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": True,
                },
            )
            logger.debug("Access token is valid")
            return True
        except Exception:
            logger.info("Failed to jwt.decode access token from cache.")
            return False

    def store_token(self, id_token, access_token, refresh_token):
        if self._no_cache == False:
            logger.debug("Storing token in disk cache")
            self._db.store_token_in_db(id_token, access_token, refresh_token)
        else:
            logger.debug("Storing of tokens to disk is disabled")

    def delete_tokens(self):
        """
        Delete on disk and in-memory tokens
        """
        self._db.delete_token_from_db()
        self.id_token = None
        self.access_token = None
        self.refresh_token = None

    def delete_access_token(self):
        """
        Delete on-disk and in-memory access token while keeping refresh tokens
        """
        self._db.delete_access_token_from_db()
        self.access_token = None

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    @property
    def id_token(self):
        return self._id_token

    @id_token.setter
    def id_token(self, value):
        self._id_token = value

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = value
