import logging

from inventaire.server import endpoints
from inventaire.session import InventaireSession


class InventaireHelpers:
    """Inventaire Helpers"""

    def __init__(self, session: InventaireSession):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def create_entity_claims(
        self,
        instance_of: str | list[str],
        illustrator: str | list[str] = [],
        author: str | list[str] = [],
        editor: str | list[str] = [],
    ):
        """
        Make the claim dictionary needed to create a new entity.

        Parameters:
            instance_of (str or list[str]): Type to which this subject corresponds/belongs (e.g., 'wd:Q47461344').
            illustrator (str or list[str]): Person drawing the pictures or taking the photographs in a book or similar work.
            author (str or list[str]): Main creator(s) of a written work (use on works, not humans).
            editor (str or list[str]): Person who checks and corrects a work (such as a book, newspaper, academic journal, etc.) to comply with a rules of certain genre.

        Returns:
            dict: Returns claim dictionary needed for api.entities.create_entity.
        """

        instance_of = [instance_of] if isinstance(instance_of, str) else instance_of
        illustrator = [illustrator] if isinstance(illustrator, str) else illustrator
        author = [author] if isinstance(author, str) else author
        editor = [editor] if isinstance(editor, str) else editor
        return {
            "wdt:P31": instance_of,
            "wdt:P110": illustrator,
            "wdt:P50": author,
            "wdt:P98": editor,
        }

    def get_entity_type_of(self):
        """
        Get all available book entities.

        Returns:
            Response: The HTTP response object from the GET request.
        """
        types = "wd:Q47461344|wd:Q7725634|wd:Q1004|wd:Q725377|wd:Q25379|wd:Q49084|wd:Q8274|wd:Q562214"
        return endpoints.EntitiesEndpoints(self.session).get_entities_by_uris(
            uris=types
        )
