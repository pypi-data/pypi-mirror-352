"""
Endpoints list used in Integration Library (verb:endpoint)
"""

# Secrets
GET_SECRETS_SAFE_SECRETS = "get:secrets-safe/secrets"
GET_SECRETS_SAFE_SECRETS_SECRETID = "get:secrets-safe/secrets/{secretid}"
GET_SECRETS_SAFE_SECRETS_SECRETID_TEXT = "get:secrets-safe/secrets/{secretid}/text"
GET_SECRETS_SAFE_SECRETS_SECRETID_FILE = "get:secrets-safe/secrets/{secretid}/file"
GET_SECRETS_SAFE_FOLDERS_FOLDERID_SECRETS = (
    "get:secrets-safe/folders/{folderid}/secrets"
)
GET_SECRETS_SAFE_FOLDERS_FOLDERID_TEXT = "get:secrets-safe/folders/{folderid}/text"
GET_SECRETS_SAFE_FOLDERS_FOLDERID_FILE = "get:secrets-safe/folders/{folderid}/file"
POST_SECRETS_SAFE_FOLDERS_FOLDERID = "post:secrets-safe/folders/{folderid}/secrets"
POST_SECRETS_SAFE_FOLDERS_FOLDERID_TEXT = (
    "post:secrets-safe/folders/{folderid}/secrets/text"
)
POST_SECRETS_SAFE_FOLDERS_FOLDERID_FILE = (
    "post:secrets-safe/folders/{folderid}/secrets/file"
)
PUT_SECRETS_SAFE_SECRETS_SECRETID = "put:secrets-safe/secrets/{secretid}"
PUT_SECRETS_SAFE_SECRETS_SECRETID_TEXT = "put:secrets-safe/secrets/{secretid}/text"
PUT_SECRETS_SAFE_SECRETS_SECRETID_FILE = "put:secrets-safe/secrets/{secretid}/file"

# Folders
GET_SECRETS_SAFE_FOLDERS = "get:secrets-safe/folders"
GET_SECRETS_SAFE_FOLDERS_FOLDERID = "get:secrets-safe/folders/{folderid}"

# Managed Systems
GET_MANAGED_SYSTEMS = "get:managedsystems"
GET_MANAGED_SYSTEMS_MANAGEDSYSTEMID = "get:managedsystems/{managedsystemid}"
GET_MANAGED_SYSTEMS_ASSETID = "get:assets/{assetid}/managedsystems"
GET_MANAGED_SYSTEMS_DATABASEID = "get:databases/{databaseid}/managedsystems"
GET_MANAGED_SYSTEMS_FUNCTIONALACCOUNTID = (
    "get:functionalaccounts/{functionalaccountid}/managedsystems"
)
GET_MANAGED_SYSTEMS_WORKGROUPID = "get:workgroups/{workgroupid}/managedsystems"
POST_MANAGED_SYSTEMS_ASSETID = "post:assets/{assetid}/managedsystems"
POST_MANAGED_SYSTEMS_DATABASEID = "post:databases/{databaseid}/managedsystems"
POST_MANAGED_SYSTEMS_WORKGROUPID = "post:workgroups/{workgroupid}/managedsystems"
DELETE_MANAGED_SYSTEMS_MANAGEDSYSTEMID = "delete:managedsystems/{managedsystemid}"
PUT_MANAGED_SYSTEMS_MANAGEDSYSTEMID = "put:managedsystems/{managedsystemid}"

# Safes
GET_SECRETS_SAFE_SAFES = "get:secrets-safe/safes"
GET_SECRETS_SAFE_SAFES_ID = "get:secrets-safe/safes/{ID}"

# Assets
GET_WORKGROUPS_ID_ASSETS = "get:workgroups/{workgroupid}/assets"
GET_ASSETS_ID_ATTRIBUTES = "get:assets/{assetid}/attributes"
GET_ASSETS_ID = "get:assets/{id}"
GET_WORKGROUPS_NAME_ASSETS_NAME = "get:workgroups/{workgroupname}/assets?name"
POST_WORKGROUPS_WORKGROUPID_ASSETS = "post:workgroups/{workgroupid}/assets"

# Smart Rules
GET_SMARTRULES_ID = "get:smartrules/{id}"

# Organizations
GET_ORGANIZATIONS = "get:organizations"
GET_ORGANIZATIONS_ID = "get:organizations/{id}"
GET_ORGANIZATIONS_NAME = "get:organizations/{name}"

# Workgroups
GET_WORKGROUPS_ID = "get:workgroups/{id}"
GET_WORKGROUPS_NAME = "get:workgroups?name={name}"
GET_WORKGROUPS = "get:workgroups"
POST_WORKGROUPS = "post:workgroups"

# Databases
GET_DATABASES = "get:databases"
GET_DATABASES_ID = "get:databases/{id}"
GET_DATABASES_ASSET_ID = "get:assets/{assetid}/databases"
POST_DATABASES_ASSET_ID = "post:assets/{assetid}/databases"
PUT_DATABASES_ID = "put:databases/{id}"
DELETE_DATABASES_ID = "delete:databases/{id}"

# Address Groups
GET_ADDRESS_GROUPS = "get:addressgroups"
GET_ADDRESS_GROUPS_ID = "get:addressgroups/{id}"
GET_ADDRESS_GROUPS_NAME = "get:addressgroups/{name}"

# Users
GET_USERS = "get:users"
GET_USERS_ID = "get:users/{id}"
GET_USERS_USERGROUPID = "get:usergroups/{usergroupid}/users"
POST_USERS_USERGROUPID = "post:usergroups/{usergroupid}/users"
POST_USERS_BI = "post:users:bi"
POST_USERS_AD = "post:users:ad"
POST_USERS_LDAP = "post:users:ldap"
POST_USERS_APP = "post:users:app"
POST_USERS_QUARANTINE = "post:users/{id}/quarantine"
POST_USERS_RECYCLE_CLIENT_SECRET = (
    "post:users/{id}/recycleclientsecret"  # nosec # noqa: S105
)
PUT_USERS_ID_BI = "put:users/{id}:bi"
PUT_USERS_ID_APP = "put:users/{id}:app"

# Managed Accounts
GET_MANAGED_SYSTEMS_SYSTEM_ID_MANAGED_ACCOUNTS = (
    "get:managedsystems/{systemid}/managedaccounts"
)
GET_MANAGED_ACCOUNTS_ID = "get:managedaccounts/{id}"

# Entitlements
GET_ENTITLEMENTS = "get:entitlements"
GET_ENTITLEMENTS_GROUP_IDS = "get:entitlements:groupids"

# Entity Types
GET_ENTITY_TYPES = "get:entitytypes"
