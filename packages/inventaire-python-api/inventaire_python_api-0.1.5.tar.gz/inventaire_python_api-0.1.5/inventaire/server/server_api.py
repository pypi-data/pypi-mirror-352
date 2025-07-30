import logging

from inventaire.server import endpoints
from inventaire.session import InventaireSession


# pylint: disable=missing-function-docstring
class InventaireApiWrapper:
    """Inventaire API wrapper"""

    def __init__(self, session: InventaireSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    @property
    def auth(self):
        return endpoints.AuthEndpoints(self.session)

    @property
    def user(self):
        return endpoints.UserEndpoints(self.session)

    @property
    def items(self):
        return endpoints.ItemsEndpoints(self.session)

    @property
    def entities(self):
        return endpoints.EntitiesEndpoints(self.session)

    @property
    def users(self):
        return endpoints.UsersEndpoints(self.session)

    @property
    def groups(self):
        return endpoints.GroupsEndpoints(self.session)

    @property
    def transactions(self):
        return endpoints.TransactionsEndpoints(self.session)

    @property
    def search(self):
        return endpoints.SearchEndpoints(self.session)

    @property
    def shelves(self):
        return endpoints.ShelvesEndpoints(self.session)

    @property
    def data(self):
        return endpoints.DataEndpoints(self.session)
