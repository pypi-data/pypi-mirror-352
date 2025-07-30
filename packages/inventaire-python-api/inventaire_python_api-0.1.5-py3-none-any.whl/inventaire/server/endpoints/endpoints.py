import copy

from inventaire.session import InventaireSession
from inventaire.utils.common import dict_merge, str_bool

from .paths import InventairePaths as Paths


class EndpointTemplate:
    """Class with basic constructor for endpoint classes"""

    def __init__(self, session: InventaireSession):
        self.session = session


class AuthEndpoints(EndpointTemplate):
    """
    Api wrapper for Auth. Login and stuffs. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/auth/auth.js
    """

    def login_user(self, username: str, password: str):
        """
        Authenticate a user with the provided credentials.

        Args:
            username (str): The user's username.
            password (str): The user's password.

        Returns:
            Response: The response object resulting from the POST request to the authentication endpoint.
        """
        json = {"username": username, "password": password}
        return self.session.post(Paths.AUTH, json=json)


class UserEndpoints(EndpointTemplate):
    """
    Api wrapper for Users. Read and edit authentified user data. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/user/user.js
    """

    def get_authentified_user(self):
        """
        Get the authentified user data.

        Returns:
            Response: The response object from the GET request.
        """
        return self.session.get(Paths.USERS)

    def update_authentified_user(self, attribute: str, value: str):
        """
        Update the authentified user.

        Args:
            attribute (str): The attribute to update (username, email, language, bio, settings, position).
            value (str): The new value to give to this attribute.

        Returns:
            Response: The response object from the PUT request.
        """
        json = {"attribute": attribute, "value": value}
        return self.session.put(Paths.USERS, json=json)


class ItemsEndpoints(EndpointTemplate):
    """
    Api wrapper for Items. What users' inventories are made of. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/items/items.js
    """

    def create_item(
        self,
        entity: str,
        transaction: str = "inventorying",
        listing: str = "private",
        lang: str | None = None,
        details: str | None = None,
        notes: str | None = None,
        data: dict | None = None,
    ):
        """
        Create an item.

        Parameters:
            entity (str): The associated book entity (work or edition) uri (e.g. 'isbn:9782253138938').
            transaction (str): The item transaction: one of giving, lending, selling, or inventorying. Defaults to inventorying.
            listing (str): The item visibility listing: one of private, network, or public. Defaults to private.
            lang (str, optional): 2-letters language code.
            details (str, optional): Free text to be visible by anyone allowed to see the item.
            notes (str, optional): Free text that is visible only by the item owner.
            data (dict, optional): Additional parameters to include in the request.

        Returns:
            Response: The HTTP response object from the POST request.
        """
        if data is None:
            data = {}

        json = {
            "entity": entity,
            **{
                k: v
                for k, v in {
                    "transaction": transaction,
                    "listing": listing,
                    "lang": lang,
                    "details": details,
                    "notes": notes,
                }.items()
                if v is not None
            },
        }
        json = dict_merge(data, json)
        return self.session.post(Paths.ITEMS, json=json)

    def update_item(self, **params):
        """
        Update an item.
        """
        raise NotImplementedError

    def get_items_by_ids(self, **params):
        """
        Items by ids.
        """
        raise NotImplementedError

    def get_items_by_users(self, **params):
        """
        Items by users ids.
        """
        raise NotImplementedError

    def get_items_by_entities(self, **params):
        """
        Items by entities URIs.
        """
        raise NotImplementedError

    def get_last_public_items(self, **params):
        """
        Last public items.
        """
        return self.session.get(Paths.ITEMS_LAST_PUBLIC, params=params)

    def get_nearby_items(self, **params):
        """
        Last nearby items.
        """
        raise NotImplementedError

    def delete_item(self, **params):
        """
        Delete an item.
        """
        raise NotImplementedError


class EntitiesEndpoints(EndpointTemplate):
    """
    Api wrapper for Entities. Think books, authors, series data. See:
    - entities map: https://inventaire.github.io/entities-map/
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/entities/entities.js
    """

    def create_entity(
        self,
        labels: dict,
        claims: dict,
        data: dict | None = None,
    ):
        """
        Create an entity.

        Parameters:
            labels (dict): An object with lang as key, and the associated label as value. e.g.:
                {
                  "en": "that entity's label in English",
                  "fr": "le label de cette entité en français"
                }
            claims (dict): An object with properties URIs as keys, and, as value, the associated array of claim values. e.g.:
                { "wdt:P31": [ "wd:Q571" ] }
            data (dict, optional): Additional parameters to include in the request.

        Returns:
            Response: The HTTP response object from the POST request.
        """
        if data is None:
            data = {}

        json = {"labels": labels, "claims": claims}
        json = dict_merge(data, json)
        return self.session.post(Paths.ENTITY_CREATE, json=json)

    def resolve_entity(
        self,
        entries: list,
        create: bool = True,
        update: bool = True,
        enrich: bool = True,
        data: dict | None = None,
    ):
        """
        Find if some entries match existing entities, and optionnaly update and/or enrich the existing entities, and/or create the missing ones.

        Parameters:
            entries (list): An object with a key "entries" and an array of objects as value. Each object can contain keys "edition", "works" and/or "authors". "edition" must be an object. "works" and "authors" must be arrays of one or several objects.
            create (bool, optional): If True, non-resolved entities will be created.
            update (bool, optional): If True, resolved entities will be updated.
            enrich (bool, optional): If True, resolved entities might be enriched with corresponding data found from other data sources. For instance an edition cover might be added, based on the provided ISBN.
            data (dict, optional): Additional parameters to include in the request.

        Returns:
            Response: The HTTP response object from the POST request.
        """
        if data is None:
            data = {}

        params = {
            "entries": entries,
            **{
                k: v
                for k, v in {
                    "create": str_bool(create),
                    "update": str_bool(update),
                    "enrich": str_bool(enrich),
                }.items()
                if v is not None
            },
        }
        params = dict_merge(data, params)
        return self.session.post(Paths.ENTITY_RESOLVE, json=params)

    def update_label(self, **params):
        """
        Update an entity's label.
        """
        raise NotImplementedError

    def update_claim(
        self,
        uri: str,
        property: str,
        old_value: str | None = None,
        new_value: str | None = None,
    ):
        """
        Update an entity's claim.

        Parameters:
            uri (str): An entity URI (e.g. 'wd:Q2196')
            property (str): The claim's property URI (e.g. 'wdt:P50')
            old_value (str, optional): The old value to be replaced. Can be omitted when intenting to create a new claim (e.g. 'wd:Q571')
            new_value (str, optional): The new value to be replaced. Can be omitted when intenting to delete a claim. (e.g. 'wd:Q2831984')

        Returns:
            Response: The response object to the PUT request.
        """
        params = {
            "uri": uri,
            "property": property,
            **{
                k: v
                for k, v in {
                    "old-value": old_value,
                    "new-value": new_value,
                }.items()
                if v is not None
            },
        }
        return self.session.put(Paths.ENTITY_UPDATE_CLAIM, json=params)

    def revert_merge(self, **params):
        """
        Revert a merge. Requires to have dataadmin rights.
        """
        raise NotImplementedError

    def get_entities_by_uris(
        self,
        uris: str,
        refresh: bool | None = None,
        autocreate: bool | None = None,
        data: dict | None = None,
    ):
        """
        Get entities by URIs.

        Parameters:
            uris (str): A title, author, or ISBN (e.g. 'wd:Q3203603|isbn:9782290349229')
            refresh (bool, optional): Request non-cached data.
            autocreate (bool, optional): If True, create an item if it doesn't exist.
            data (dict, optional): Additional parameters to include in the request.

        Returns:
            Response: The response object from the GET request.
        """
        if data is None:
            data = {}

        params = {
            "uris": uris,
            **{
                k: v
                for k, v in {
                    "refresh": str_bool(refresh),
                    "autocreate": str_bool(autocreate),
                }.items()
                if v is not None
            },
        }
        params = dict_merge(data, params)
        return self.session.get(Paths.ENTITY_BY_URIS, params=params)

    def get_entities_by_claims(self, **params):
        """
        Get entities URIs by their claims.
        """
        raise NotImplementedError

    def get_popularity(self, uris: str | list[str], refresh: bool = False):
        """
        Get popularity score of an entity.

        Args:
            uris (str or list[str]): A title, author, or ISBN separated by pipes or a list of elements (e.g., 'wd:Q3203603|isbn:9782290349229|inv:d59e3e64f92c6340fbb10c5dcf437d86').
            refresh (bool, optional): Request non-cached data. Defaults to 'False'.

        Returns:
            Response: The response object from the GET request.
        """
        params = {"uris": "|".join(uris) if isinstance(uris, list) else uris}
        if refresh:
            params["refresh"] = str_bool(refresh)
        return self.session.get(Paths.ENTITY_POPULARITY, params=params)

    def get_history(self, id: str):
        """
        Get entities history as snapshots and diffs.

        Args:
            id (str): An (internal) entity id (e. g., 'd59e3e64f92c6340fbb10c5dcf437d86').

        Returns:
            Response: The response object from the GET request.
        """
        params = {"id": id}
        return self.session.get(Paths.ENTITY_HISTORY, params=params)

    def get_author_works(self, uri: str, refresh: bool = False):
        """
        Pass an author URI, get uris of all works, series and articles of the entity that match this claim

        Args:
            uri (str): An author URI (e. g. 'wd:Q2196').
            refresh (bool, optional): Request non-cached data. Defaults to 'False'.

        Returns:
            Response: The response object from the GET request.
        """
        params = {"uri": uri}
        if refresh:
            params["refresh"] = str_bool(refresh)
        return self.session.get(Paths.ENTITY_AUTHOR_WORKS, params=params)

    def get_serie_parts(self, uri: str, refresh: bool = False):
        """
        Get a serie's parts.

        Args:
            uri (str): A serie URI (e. g. 'wd:Q718449').
            refresh (bool, optional): Request non-cached data. Defaults to 'False'.

        Returns:
            Response: The response object from the GET request.
        """
        params = {"uri": uri}
        if refresh:
            params["refresh"] = str_bool(refresh)
        return self.session.get(Paths.ENTITY_SERIE_PARTS, params=params)

    def get_publisher_publications(self, **params):
        """
        Get the publications of a publisher.
        """
        raise NotImplementedError

    def revert_edit(self, **params):
        """
        Revert an entity edit.
        """
        raise NotImplementedError

    def restore_version(self, **params):
        """
        Restores an entity to a past version.
        """
        raise NotImplementedError

    def move_to_wikidata(self, uri: str):
        """
        Move an inventaire entity to Wikidata.

        Args:
            uri (str): Entity URI (e.g., 'inv:60044095fc153704829f47af07a1517e').

        Returns:
            Response: The response object resulting from the GET request to the shelves endpoint.
        """
        json = {"uri": uri}
        return self.session.put(Paths.ENTITY_MOVE_WIKIDATA, json=json)


class UsersEndpoints(EndpointTemplate):
    """
    Api wrapper for Users. Read and edit authentified user data. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/users/users.js
    """

    def get_users_by_ids(self, ids: str | list[str]):
        """
        Users by ids.

        Args:
            ids (str or list[str]): Ids separated by pipes as a string or a list ids.

        Returns:
            Response: The response object resulting from the GET request.
        """
        ids_str = "|".join(ids) if isinstance(ids, list) else ids
        return self.session.get(Paths.USERS_BY_IDS, params={"ids": ids_str})

    def get_users_by_usernames(self, usernames: str | list[str]):
        """
        Users by usernames.

        Args:
            usernames (str or list[str]): Usernames separated by pipes as a string or a list usernames.

        Returns:
            Response: The response object resulting from the GET request.
        """
        users_str = "|".join(usernames) if isinstance(usernames, list) else usernames
        return self.session.get(
            Paths.USERS_BY_USERNAMES, params={"usernames": users_str}
        )

    def search(self, search):
        """
        Search users.

        Args:
            search (str): Text matching users username or bio.

        Returns:
            Response: The response object from the GET request.
        """
        params = {"search": search}
        return self.session.get(Paths.USERS_SEARCH, params=params)


class GroupsEndpoints(EndpointTemplate):
    """
    Api wrapper for Groups. Read and edit users groups data. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/groups/groups.js
    """

    def get_groups(self, **params):
        """
        Get all the groups the authentified user is a member of.

        Returns:
            Response: The response object from the GET request.
        """
        return self.session.get(Paths.GROUPS)

    def get_group_by_id(self, id: str):
        """
        Get a group by its id.

        Args:
            id (str): A group id (e. g. '85d797f862e362335f3e6144cc12568a').

        Returns:
            Response: The response object from the GET request.
        """
        params = {"id": id}
        return self.session.get(Paths.GROUPS_BY_ID, params=params)

    def get_group_by_slug(self, slug: str):
        """
        Get a group by its slug.

        Args:
            slug (str): A group slug (e. g. 'la-myne').

        Returns:
            Response: The response object from the GET request.
        """
        params = {"slug": slug}
        return self.session.get(Paths.GROUPS_BY_SLUG, params=params)

    def get_groups_by_username(self, **params):
        """
        Groups by usernames.
        """
        raise NotImplementedError

    def invite(self, **params):
        """
        Invite a user to join the group.
        """
        raise NotImplementedError

    def accept(self, **params):
        """
        Accept an invitation to join a group.
        """
        raise NotImplementedError

    def decline(self, **params):
        """
        Decline an invitation to join a group.
        """
        raise NotImplementedError

    def request(self, **params):
        """
        Request to join the group.
        """
        raise NotImplementedError

    def cancel_request(self, **params):
        """
        Cancel the authentified user request to join a group.
        """
        raise NotImplementedError

    def accept_request(self, **params):
        """
        Accept a user request to join the group.
        """
        raise NotImplementedError

    def refuse_request(self, **params):
        """
        Refuse a user request to join the group.
        """
        raise NotImplementedError

    def make_admin(self, **params):
        """
        Give admin right to a non-admin member.
        """
        raise NotImplementedError

    def kick(self, **params):
        """
        Remove a user from the group.
        """
        raise NotImplementedError

    def leave_group(self, **params):
        """
        Leave a group.
        """
        raise NotImplementedError

    def update_group_settings(self, **params):
        """
        Update the group settings.
        """
        raise NotImplementedError


class TransactionsEndpoints(EndpointTemplate):
    """
    Api wrapper for Transactions. When users request each others items. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/transactions/transactions.js
    """

    def get_transactions(self):
        """
        Get the authentified user transactions data.

        Returns:
            Response: The response object resulting from the GET request to the shelves endpoint.
        """
        return self.session.get(Paths.TRANSACTIONS)

    def get_transaction_messages(self, transaction: str):
        """
        Get messages associated to a transaction.

        Args:
            transaction (str): A transaction id (e. g., '85d797f862e362335f3e6144cc12568a').

        Returns:
            Response: The response object from the GET request.
        """
        params = {"transaction": transaction}
        return self.session.get(Paths.TRANSACTIONS_MESSAGES, params=params)


class SearchEndpoints(EndpointTemplate):
    """
    Api wrapper for Search. The generalist search endpoint. See:
    - code: https://github.com/inventaire/inventaire/blob/master/server/controllers/search/search.js
    """

    def search(
        self,
        search: str,
        types: str = "works|series|humans",
        limit: int | None = None,
        lang: str | None = None,
        exact: bool | None = None,
        min_score: int | None = None,
        data: dict | None = None,
    ):
        """
        Search for entities (works, humans, genres, publishers, series, collections), users, or groups.

        Parameters:
            search (str): The search term or query string.
            types (str): A pipe-separated string of entity types to search for
                         (possible values: works, humans, genres, publishers, series, collections, genres, movements, languages, users, groups, shelves, lists). Defaults to "works|series|humans".
            limit (int, optional): Maximum number of results to return.
            lang (str, optional): Language code to filter results by language.
            exact (bool, optional): If True, perform an exact match search.
            min_score (int, optional): Minimum relevance score for filtering results.
            data (dict, optional): Additional parameters to include in the request.

        Returns:
            Response: The HTTP response object from the POST request.
        """
        if data is None:
            data = {}

        params = {
            "search": search,
            "types": types,
            **{
                k: v
                for k, v in {
                    "limit": limit,
                    "lang": lang,
                    "exact": str_bool(exact),
                    "min_score": min_score,
                }.items()
                if v is not None
            },
        }
        params = dict_merge(data, params)
        return self.session.get(Paths.SEARCH, params=params)


class ShelvesEndpoints(EndpointTemplate):
    """
    Api wrapper for Shelves. List of items.
    Items must belong to the shelf' owner.
    An owner can add or remove items from their own shelf.
    An owner must be a user.
    """

    def get_shelves_by_ids(self, ids: str | list[str]):
        """
        Retrieve shelf data for the given shelf IDs.

        Args:
            ids (str or list[str]): A shelf ID separated by pipes as a string or a list of shelf IDs.

        Returns:
            Response: The response object resulting from the GET request to the shelves endpoint.
        """
        ids_str = "|".join(ids) if isinstance(ids, list) else ids
        return self.session.get(Paths.SHELVES_BY_IDS, params={"ids": ids_str})

    def get_shelves_by_owners(self, owners: str | list[str]):
        """
        Retrieve shelf data for the given owners ID.

        Args:
            ids (str or list[str]): A owner ID separated by pipes as a string or a list of owner IDs.

        Returns:
            Response: The response object resulting from the GET request to the shelves endpoint.
        """
        owners_str = "|".join(owners) if isinstance(owners, list) else owners
        return self.session.get(Paths.SHELVES_BY_OWNERS, params={"owners": owners_str})

    def create_shelf(
        self, name: str, listing: str, description: str, data: dict | None = None
    ):
        """
        Create a new shelf with the given details.

        Args:
            name (str): The name of the shelf.
            listing (str): The shelf visibility listing: one of private, network, or public.
            description (str): A description of the shelf.
            data (dict, optional): Additional data to merge into the request payload.

        Returns:
            Response: The response object resulting from the POST request to create the shelf.
        """
        if data is None:
            data = {}

        json = {"name": name, "listing": listing, "description": description}
        merged_json = dict_merge(data, json)
        return self.session.post(Paths.SHELVES_CREATE, json=merged_json)

    def update_shelf(
        self,
        id: str,
        name: str,
        listing: str,
        description: str | None = None,
        data: dict | None = None,
    ):
        """
        Update an existing shelf with the given details.

        Args:
            id (str): The shelf ID.
            name (str): The name of the shelf.
            listing (str): The shelf visibility listing: one of private, network, or public.
            description (str, optional): A description of the shelf.
            data (dict, optional): Additional data to merge into the request payload.

        Returns:
            Response: The response object resulting from the POST request to create the shelf.
        """
        if data is None:
            data = {}

        json = {"id": id, "name": name, "listing": listing}
        if description:
            json["description"] = description
        merged_json = dict_merge(data, json)
        return self.session.post(Paths.SHELVES_UPDATE, json=merged_json)

    def delete_shelf(self, id: str, data: dict | None = None):
        """
        Delete an existing shelf.

        Args:
            id (str): The shelf ID.
            data (dict, optional): Additional data to merge into the request payload.

        Returns:
            Response: The response object resulting from the POST request to create the shelf.
        """
        if data is None:
            data = {}

        json = {"id": id}
        merged_json = dict_merge(data, json)
        return self.session.post(Paths.SHELVES_DELETE, json=merged_json)

    def add_items(self, **params):
        """
        Add items to a shelf.
        """
        raise NotImplementedError

    def remove_items(self, **params):
        """
        Remove items from a shelf.
        """
        raise NotImplementedError


class DataEndpoints(EndpointTemplate):
    """
    Api wrapper for Data.
    """

    def request_extract_wikipedia(self, title: str, lang: str | None = None):
        """
        Request a summary extract from Wikipedia for a given article title and language.

        Args:
            title (str): The title of the Wikipedia article.
            lang (str, optional): The language code (e.g., 'en', 'fr') for the Wikipedia edition.

        Returns:
            Response: The response object from the GET request to retrieve the extract.
        """
        params = {"title": title}
        if lang:
            params["lang"] = lang
        return self.session.get(Paths.DATA_WP_EXTRACT, params=params)

    def get_isbn_basic_facts(self, isbn: str):
        """
        An endpoint to get basic facts from an ISBN.

        Args:
            isbn (str): 10 or 13, with or without hyphen.

        Returns:
            Response: The response object from the GET request.
        """
        params = {"isbn": isbn}
        return self.session.get(Paths.DATA_ISBN, params=params)

    def get_property_values(self, property: str, type: str):
        """
        Return the allowed values per type for a given property.

        Args:
            property (str): A property (e. g., 'wdt:P31').
            type (str): A type from lib/wikidata/aliases (e. g., 'series').

        Returns:
            Response: The response object from the GET request.
        """
        params = {"property": property, "type": type}
        return self.session.get(Paths.DATA_PROPERTY_VALUES, params=params)
