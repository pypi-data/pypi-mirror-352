from statql.common import PluginBlueprint
from .connector import Neo4jConnector
from .definitions import Neo4jIntegrationDetails
from .fe_controller import Neo4jFEController

NEO4J_BLUEPRINT = PluginBlueprint(
    catalog_name="neo",
    fe_controller_cls=Neo4jFEController,
    connector_cls=Neo4jConnector,
    integration_details_cls=Neo4jIntegrationDetails,
)
