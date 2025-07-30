"""Paths to form Server API URLs"""


class InventairePaths:
    """
    Inventaire paths based on: https://api.inventaire.io
    """

    # Auth
    AUTH = "auth?action=login"

    # Users
    USERS = "user"

    # Items
    ITEMS = "items"
    ITEMS_BY_IDS = "items?action=by-ids"
    ITEMS_BY_USERS = "items?action=by-users"
    ITEMS_BY_ENTITIES = "items?action=by-entities"
    ITEMS_LAST_PUBLIC = "items?action=last-public"
    ITEMS_NEARBY = "items?action=nearby"

    # Entities
    ENTITY_CREATE = "entities?action=create"
    ENTITY_RESOLVE = "entities?action=resolve"
    ENTITY_UPDATE_LABEL = "entities?action=update-label"
    ENTITY_UPDATE_CLAIM = "entities?action=update-claim"
    ENTITY_REVERT_MERGE = "entities?action=revert-merge"
    ENTITY_BY_URIS = "entities?action=by-uris"
    ENTITY_LAST_CHANGES = "entities?action=changes"
    ENTITY_REVERSE_CLAIMS = "entities?action=reverse-claims"
    ENTITY_POPULARITY = "entities?action=popularity"
    ENTITY_HISTORY = "entities?action=history"
    ENTITY_AUTHOR_WORKS = "entities?action=author-works"
    ENTITY_SERIE_PARTS = "entities?action=serie-parts"
    ENTITY_PUBLISHER = "entities?action=publisher-publications"
    ENTITY_REVERT_EDIT = "entities?action=revert-edit"
    ENTITY_RESTORE_VERSION = "entities?action=restore-version"
    ENTITY_MOVE_WIKIDATA = "entities?action=move-to-wikidata"

    # Users
    USERS_BY_IDS = "users?action=by-ids"
    USERS_BY_USERNAMES = "users?action=by-usernames"
    USERS_SEARCH = "users?action=search"

    # Groups
    GROUPS = "groups"
    GROUPS_BY_ID = "groups?action=by-id"
    GROUPS_BY_SLUG = "groups?action=by-slug"
    GROUPS_SEARCH = "groups?action=search"
    GROUPS_CREATE = "groups?action=create"
    GROUPS_INVITE = "groups?action=invite"
    GROUPS_ACCEPT = "groups?action=accept"
    GROUPS_DECLINE = "groups?action=decline"
    GROUPS_REQUEST = "groups?action=request"
    GROUPS_CANCEL_REQUEST = "groups?action=cancel-request"
    GROUPS_ACCEPT_REQUEST = "groups?action=accept-request"
    GROUPS_REFUSE_REQUEST = "groups?action=refuse-request"
    GROUPS_MAKE_ADMIN = "groups?action=make-admin"
    GROUPS_KICK = "groups?action=kick"
    GROUPS_LEAVE = "groups?action=leave"
    GROUPS_UPDATE_SETTINGS = "groups?action=update-settings"

    # Transactions
    TRANSACTIONS = "transactions"
    TRANSACTIONS_MESSAGES = "transactions?action=get-messages"

    # Search
    SEARCH = "search"

    # Shelves
    SHELVES_BY_IDS = "shelves?action=by-ids"
    SHELVES_BY_OWNERS = "shelves?action=by-owners"
    SHELVES_CREATE = "shelves?action=create"
    SHELVES_UPDATE = "shelves?action=update"
    SHELVES_DELETE = "shelves?action=delete"
    SHELVES_ADD_ITEMS = "shelves?action=add-items"
    SHELVES_REMOVE_ITEMS = "shelves?action=remove-items"

    # Data
    DATA_WP_EXTRACT = "data?action=wp-extract"
    DATA_ISBN = "data?action=isbn"
    DATA_PROPERTY_VALUES = "data?action=property-values"
