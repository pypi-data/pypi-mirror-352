import typing

import streamlit as st

from statql.common import IFEController, ISecretsManager
from .definitions import Neo4jIntegrationDetails, Neo4jConnectorConfig


class Neo4jFEController(IFEController[Neo4jIntegrationDetails, Neo4jConnectorConfig]):
    title = "🧫 Neo4j"

    @classmethod
    def get_integration_form(cls) -> typing.Dict:
        return {
            "uri": st.text_input("URI (e.g., bolt://localhost:7687)"),
            "username": st.text_input("Username"),
            "password": st.text_input("Password", type="password"),
        }

    @classmethod
    def build_integration_details(
        cls, *, integration_name: str, integration_form_input: typing.Mapping[str, typing.Any], secrets_manager: ISecretsManager
    ) -> Neo4jIntegrationDetails:
        secret_name = secrets_manager.store_secret(
            secret_name_prefix=f"neo4j-password-{integration_name}",
            secret_value=integration_form_input["password"],
        )

        return Neo4jIntegrationDetails(
            uri=integration_form_input["uri"],
            user=integration_form_input["username"],
            password_secret_name=secret_name,
        )

    @classmethod
    def verify_new_integration(cls, *, new_integration: Neo4jIntegrationDetails, existing_integrations: typing.Iterable[Neo4jIntegrationDetails]) -> str | None:
        if new_integration.uri in {integration.uri for integration in existing_integrations}:
            return "URI is already integrated"

    @classmethod
    def build_connector_config(cls, *, integration_details: Neo4jIntegrationDetails, secrets_manager: ISecretsManager) -> Neo4jConnectorConfig:
        return Neo4jConnectorConfig(
            uri=integration_details.uri,
            user=integration_details.user,
            password=secrets_manager.get_secret(secret_name=integration_details.password_secret_name),
        )

    @classmethod
    def get_fe_details(cls, *, integration_details: Neo4jIntegrationDetails) -> typing.List[typing.Tuple[str, str]]:
        return [
            ("URI", integration_details.uri),
            ("Username", integration_details.user),
        ]
