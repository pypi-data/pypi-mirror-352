import asyncio
import typing
from datetime import timedelta

import numpy as np
from neo4j import AsyncGraphDatabase
from pandas import DataFrame

from statql.common import TableInfo, IAsyncConnector, ICache, StatQLInternalColumns
from .client import Neo4jClient
from .definitions import Neo4jConnectorConfig, Neo4jTableIdentifier, Neo4jTableCategories, Neo4jTableMetaColumnNames


class Neo4jConnector(IAsyncConnector[Neo4jConnectorConfig, Neo4jTableIdentifier]):
    def __init__(self, *, cache: ICache, config: Neo4jConnectorConfig):
        super().__init__(cache=cache, config=config)
        self._connection = AsyncGraphDatabase.driver(
            uri=self._config.uri,
            auth=(self._config.user, self._config.password),
        )

    async def resolve_table_path(self, *, table_path: typing.Sequence[str]) -> typing.AsyncGenerator[Neo4jTableIdentifier, None]:
        db_name, category, table_name = table_path

        # Try to get database names from cache first
        try:
            db_names = await asyncio.to_thread(self._cache.fetch, key="db_names")
        except LookupError:
            db_names = await Neo4jClient.get_databases(connection=self._connection)
            await asyncio.to_thread(self._cache.store, key="db_names", value=db_names, ttl=timedelta(hours=24))

        if db_name == "?":
            matching_db_names = db_names
        else:
            matching_db_names = {db_name} if db_name in db_names else set()

        for matching_db_name in matching_db_names:
            yield Neo4jTableIdentifier(db_name=matching_db_name, category=category, table_name=table_name)

    async def scan_table(self, *, table: Neo4jTableIdentifier, columns: typing.AbstractSet[str]) -> typing.AsyncGenerator[DataFrame, None]:
        if table.category == Neo4jTableCategories.NODES:
            row_number = 0

            async for df in Neo4jClient.scan_label(
                label=table.table_name,
                properties=columns - set(Neo4jTableMetaColumnNames),
                chunk_size=self._config.scan_chunk_size,
                connection=self._connection,
                db=table.db_name,
            ):
                # Adding internal columns (required by infra)
                df[StatQLInternalColumns.ROW_ID] = np.arange(row_number, row_number + len(df))
                row_number += len(df)

                # Adding meta columns if requested
                if Neo4jTableMetaColumnNames.DB_NAME in columns:
                    df[Neo4jTableMetaColumnNames.DB_NAME] = table.db_name

                yield df

        elif table.category == Neo4jTableCategories.RELS:
            row_number = 0

            async for df in Neo4jClient.scan_relationship_type(
                rel_type=table.table_name,
                properties=columns - set(Neo4jTableMetaColumnNames),
                chunk_size=self._config.scan_chunk_size,
                connection=self._connection,
                db=table.db_name,
            ):
                # Adding internal columns (required by infra)
                df[StatQLInternalColumns.ROW_ID] = np.arange(row_number, row_number + len(df))
                row_number += len(df)

                # Adding meta columns if requested
                if Neo4jTableMetaColumnNames.DB_NAME in columns:
                    df[Neo4jTableMetaColumnNames.DB_NAME] = table.db_name

                yield df

        else:
            raise NotImplementedError

    async def estimate_row_count(self, *, table: Neo4jTableIdentifier) -> int:
        # Try to get row count from cache first
        try:
            return await asyncio.to_thread(self._cache.fetch, key=f"table_row_count.{table}")
        except LookupError:
            if table.category == Neo4jTableCategories.NODES:
                cnt = await Neo4jClient.count_label(label=table.table_name, connection=self._connection, db=table.db_name)
            elif table.category == Neo4jTableCategories.RELS:
                cnt = await Neo4jClient.count_relationship_type(rel_type=table.table_name, connection=self._connection, db=table.db_name)
            else:
                raise NotImplementedError

            # Store the count in cache for future use
            await asyncio.to_thread(self._cache.store, key=f"table_row_count.{table}", value=cnt, ttl=timedelta(hours=24))
            return cnt

    async def _get_cached_or_fetch(self, *, cache_key: str, fetch_func: typing.Callable) -> typing.Any:
        try:
            return await asyncio.to_thread(self._cache.fetch, key=cache_key)
        except LookupError:
            value = await fetch_func()
            await asyncio.to_thread(self._cache.store, key=cache_key, value=value, ttl=timedelta(hours=24))
            return value

    async def fetch_all_tables(self) -> typing.AsyncGenerator[TableInfo, None]:
        # Get database names (using cache if available)
        db_names = await self._get_cached_or_fetch(cache_key="db_names", fetch_func=lambda: Neo4jClient.get_databases(connection=self._connection))

        all_tables = []

        for db_name in db_names:
            labels = await self._get_cached_or_fetch(
                cache_key=f"{db_name}.labels", fetch_func=lambda: Neo4jClient.get_labels(connection=self._connection, db=db_name)
            )

            for label in labels:
                label_field_names = await self._get_cached_or_fetch(
                    cache_key=f"{db_name}.label.{label}.fields",
                    fetch_func=lambda l=label: Neo4jClient.get_label_fields(label=l, connection=self._connection, db=db_name),
                )

                table_info = TableInfo(
                    path=[db_name, Neo4jTableCategories.NODES, label],
                    columns=set(label_field_names) | set(Neo4jTableMetaColumnNames),
                )
                all_tables.append({"path": table_info.path, "columns": list(table_info.columns)})
                yield table_info

            rel_types = await self._get_cached_or_fetch(
                cache_key=f"{db_name}.rel_types", fetch_func=lambda: Neo4jClient.get_relationship_types(connection=self._connection, db=db_name)
            )

            for rel_type in rel_types:
                rel_field_names = await self._get_cached_or_fetch(
                    cache_key=f"{db_name}.rel.{rel_type}.fields",
                    fetch_func=lambda rt=rel_type: Neo4jClient.get_relationship_type_fields(rel_type=rt, connection=self._connection, db=db_name),
                )

                table_info = TableInfo(
                    path=[db_name, Neo4jTableCategories.RELS, rel_type],
                    columns=set(rel_field_names) | set(Neo4jTableMetaColumnNames),
                )
                all_tables.append({"path": table_info.path, "columns": list(table_info.columns)})
                yield table_info

    async def close(self) -> None:
        await self._connection.close()
