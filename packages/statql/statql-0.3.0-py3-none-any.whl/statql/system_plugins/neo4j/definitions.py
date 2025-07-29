import enum

from statql.common import IConnectorConfig, IIntegrationDetails, FrozenModel


BLACKLISTED_DATABASES = {"system"}


class Neo4jConnectorConfig(IConnectorConfig):
    uri: str
    user: str
    password: str
    scan_chunk_size: int = 10000


class Neo4jIntegrationDetails(IIntegrationDetails):
    uri: str
    user: str
    password_secret_name: str


class Neo4jTableCategories(enum.StrEnum):
    NODES = "nodes"
    RELS = "rels"


class Neo4jTableMetaColumnNames(enum.StrEnum):
    DB_NAME = "@db"


class Neo4jTableIdentifier(FrozenModel):
    db_name: str
    category: Neo4jTableCategories
    table_name: str
