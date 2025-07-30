"""
A module with the Inventaire base object.
"""

import logging

from inventaire.server.helpers import InventaireHelpers
from inventaire.server.server_api import InventaireApiWrapper
from inventaire.session import InventaireSession

DEFAULT_BASE_URL = "https://inventaire.io/api/"


class Inventaire:
    """
    Inventaire base object to interact with other objects or raw api
    by its methods.

    :param base_url: base API url to connect with. An example for
                     Inventaire looks like 'https://inventaire.io/api/'
    """

    def __init__(self, base_url=None, **kwargs):
        base_url = DEFAULT_BASE_URL if not base_url else base_url

        session = InventaireSession(base_url=base_url, **kwargs)
        self.api = InventaireApiWrapper(session)
        self.api.auth.login_user(**kwargs)
        self.helpers = InventaireHelpers(session)

        self.logger = logging.getLogger(__name__)

    @classmethod
    def server_api(cls, base_url: str | None = None, **kwargs):
        """Alternative constructor for Inventaire client"""
        if base_url:
            return cls(base_url=base_url, **kwargs)
        return cls(base_url=DEFAULT_BASE_URL, **kwargs)
