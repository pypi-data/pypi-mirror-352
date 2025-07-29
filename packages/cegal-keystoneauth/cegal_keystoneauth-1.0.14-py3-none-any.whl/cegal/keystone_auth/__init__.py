# Copyright 2025 Cegal AS
# All rights reserved

__version__ = "1.0.14"
__git_hash__ = "907ddd54"

import logging
from os import getenv


logger = logging.getLogger(__name__)
verify_tls = True
if getenv("PYVAR_ALLOW_NON_HTTPS") == "true":
    verify_tls = False


from .client import OidcClient
from .options import OidcOptions, OidcFlow
