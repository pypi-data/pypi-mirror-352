import typing

import neo4j
from neo4j import AsyncDriver
from pandas import DataFrame

from statql.system_plugins.neo4j.definitions import BLACKLISTED_DATABASES


class Neo4jClient:
    @classmethod
    async def scan_label(
        cls, *, label: str, properties: typing.AbstractSet[str], chunk_size: int, connection: AsyncDriver, db: str
    ) -> typing.AsyncGenerator[DataFrame, None]:
        offset = 0
        props_str = f", ".join(f"node.{prop_name} AS {prop_name}" for prop_name in properties) if properties else "1 AS dummy"

        while True:
            async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
                result = await session.run(
                    f"""
                    MATCH (node :{label})
                    RETURN {props_str}
                    SKIP $offset LIMIT $limit
                    """,
                    offset=offset,
                    limit=chunk_size,
                )

                records = []

                async for record in result:
                    records.append(dict(record))

            df = DataFrame.from_records(records)
            yield df

            if len(records) < chunk_size:
                break

            offset += chunk_size

    @classmethod
    async def scan_relationship_type(
        cls, *, rel_type: str, properties: typing.AbstractSet[str], chunk_size: int, connection: AsyncDriver, db: str
    ) -> typing.AsyncGenerator[DataFrame, None]:
        offset = 0
        props_str = f", ".join(f"rel.{prop_name} AS {prop_name}" for prop_name in properties) if properties else "1 AS dummy"

        while True:
            async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
                result = await session.run(
                    f"""
                    MATCH ()-[rel :{rel_type}]->()
                    RETURN {props_str}
                    SKIP $offset LIMIT $limit
                    """,
                    offset=offset,
                    limit=chunk_size,
                )

                records = []

                async for record in result:
                    records.append(dict(record))

            df = DataFrame.from_records(records)
            yield df

            if len(records) < chunk_size:
                break

            offset += chunk_size

    @classmethod
    async def count_label(cls, *, label: str, connection: AsyncDriver, db: str) -> int:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run(f"MATCH (:{label}) RETURN COUNT(*) AS count")
            record = await result.single()
            count = record["count"]

            if not isinstance(count, int):
                raise TypeError(f"Expected count to be an int, got {type(count).__name__}")

            return count

    @classmethod
    async def count_relationship_type(cls, *, rel_type: str, connection: AsyncDriver, db: str) -> int:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run(f"MATCH ()-[:{rel_type}]->() RETURN COUNT(*) AS count")
            record = await result.single()
            count = record["count"]

            if not isinstance(count, int):
                raise TypeError(f"Expected count to be an int, got {type(count).__name__}")

            return count

    @classmethod
    async def get_databases(cls, *, connection: AsyncDriver) -> typing.Set[str]:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database="system") as session:
            result = await session.run("SHOW DATABASES")
            databases = {record["name"] for record in await result.data()} - BLACKLISTED_DATABASES
            return databases

    @classmethod
    async def get_labels(cls, *, connection: AsyncDriver, db: str) -> typing.Set[str]:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run("CALL db.labels()")
            labels = {record["label"] for record in await result.data()}
            return labels

    @classmethod
    async def get_label_fields(cls, *, label: str, connection: AsyncDriver, db: str) -> typing.Set[str]:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run(
                f"""
                MATCH (n:{label}) 
                WITH KEYS(n) AS node_field_names LIMIT 100
                UNWIND node_field_names AS node_field_name
                RETURN COLLECT(DISTINCT node_field_name) AS label_field_names
                """,
            )
            record = await result.single()
            return set(record["label_field_names"])

    @classmethod
    async def get_relationship_types(cls, *, connection: AsyncDriver, db: str) -> typing.Set[str]:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run("CALL db.relationshipTypes()")
            rel_types = {record["relationshipType"] for record in await result.data()}
            return rel_types

    @classmethod
    async def get_relationship_type_fields(cls, *, rel_type: str, connection: AsyncDriver, db: str) -> typing.Set[str]:
        async with connection.session(default_access_mode=neo4j.READ_ACCESS, database=db) as session:
            result = await session.run(
                f"""
                MATCH ()-[r:{rel_type}]->()
                WITH KEYS(r) AS rel_field_names LIMIT 100
                UNWIND rel_field_names AS rel_field_name
                RETURN COLLECT(DISTINCT rel_field_name) AS rel_field_names
                """,
            )
            record = await result.single()
            return set(record["rel_field_names"])
