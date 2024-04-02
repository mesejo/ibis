from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

import ibis
from ibis.backends.tests.base import BackendTest, ServiceBackendTest

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

PG_USER = os.environ.get(
    "IBIS_TEST_POSTGRES_USER", os.environ.get("PGUSER", "postgres")
)
PG_PASS = os.environ.get(
    "IBIS_TEST_POSTGRES_PASSWORD", os.environ.get("PGPASSWORD", "postgres")
)
PG_HOST = os.environ.get(
    "IBIS_TEST_POSTGRES_HOST", os.environ.get("PGHOST", "localhost")
)
PG_PORT = os.environ.get("IBIS_TEST_POSTGRES_PORT", os.environ.get("PGPORT", 5432))
IBIS_TEST_POSTGRES_DB = os.environ.get(
    "IBIS_TEST_POSTGRES_DATABASE", os.environ.get("PGDATABASE", "ibis_testing")
)


class PostgresTestConf(ServiceBackendTest):
    # postgres rounds half to even for double precision and half away from zero
    # for numeric and decimal

    returned_timestamp_unit = "s"
    supports_structs = False
    rounding_method = "half_to_even"
    service_name = "postgres"
    deps = ("psycopg2",)

    driver_supports_multiple_statements = True

    @property
    def test_files(self) -> Iterable[Path]:
        return self.data_dir.joinpath("csv").glob("*.csv")

    @staticmethod
    def connect(*, tmpdir, worker_id, **kw):
        return ibis.postgres.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASS,
            database=IBIS_TEST_POSTGRES_DB,
            **kw,
        )


@pytest.fixture(scope="session")
def postgres(tmp_path_factory, data_dir, worker_id):
    return PostgresTestConf.load_data(data_dir, tmp_path_factory, worker_id).connection


class TestConf(BackendTest):
    # check_names = False
    # supports_divide_by_zero = True
    # returned_timestamp_unit = 'ns'
    supports_structs = False
    supports_json = False
    supports_arrays = True
    stateful = False
    deps = ("datafusion",)

    @staticmethod
    def connect(*, tmpdir, worker_id, **kw):
        return ibis.meta.connect(**kw)


@pytest.fixture(scope="session")
def con(data_dir, tmp_path_factory, worker_id, postgres):
    meta = TestConf.load_data(data_dir, tmp_path_factory, worker_id).connection
    meta.add_connection(postgres)
    return meta


@pytest.fixture(scope="session")
def alltypes(con):
    return con.table("functional_alltypes")


@pytest.fixture(scope="session")
def alltypes_df(alltypes):
    return alltypes.execute()
