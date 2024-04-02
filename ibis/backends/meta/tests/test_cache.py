from __future__ import annotations

import pytest

from ibis.backends.datafusion.tests.conftest import BackendTest

pytest.importorskip("datafusion")
pytest.importorskip("psycopg2")


def test_cache_simple(con, alltypes, alltypes_df):
    expr = alltypes.select(
        alltypes.smallint_col, alltypes.int_col, alltypes.float_col
    ).filter(
        [
            alltypes.float_col > 0,
            alltypes.smallint_col == 9,
            alltypes.int_col < alltypes.float_col * 2,
        ]
    )
    cached = expr.cache()
    tables_after_caching = con.list_tables()

    expected = alltypes_df[
        (alltypes_df["float_col"] > 0)
        & (alltypes_df["smallint_col"] == 9)
        & (alltypes_df["int_col"] < alltypes_df["float_col"] * 2)
    ][["smallint_col", "int_col", "float_col"]]

    cached = cached.execute()
    tables_after_executing = con.list_tables()

    BackendTest.assert_frame_equal(cached, expected)
    assert not any(
        table_name.startswith("ibis_cache") for table_name in tables_after_caching
    )
    assert any(
        table_name.startswith("ibis_cache") for table_name in tables_after_executing
    )


def test_cache_multiple_times(con, alltypes, alltypes_df):
    expr = alltypes.select(
        alltypes.smallint_col, alltypes.int_col, alltypes.float_col
    ).filter(
        [
            alltypes.float_col > 0,
            alltypes.smallint_col == 9,
            alltypes.int_col < alltypes.float_col * 2,
        ]
    )
    cached = expr.cache()

    # reassign the expression
    expr = alltypes.select(
        alltypes.smallint_col, alltypes.int_col, alltypes.float_col
    ).filter(
        [
            alltypes.float_col > 0,
            alltypes.smallint_col == 9,
            alltypes.int_col < alltypes.float_col * 2,
        ]
    )

    recached = expr.cache()

    first = cached.execute()
    tables_after_first_caching = con.list_tables()

    second = recached.execute()
    tables_after_second_caching = con.list_tables()

    expected = alltypes_df[
        (alltypes_df["float_col"] > 0)
        & (alltypes_df["smallint_col"] == 9)
        & (alltypes_df["int_col"] < alltypes_df["float_col"] * 2)
    ][["smallint_col", "int_col", "float_col"]]

    BackendTest.assert_frame_equal(first, expected)
    BackendTest.assert_frame_equal(second, expected)

    first_tables = [t for t in tables_after_first_caching if t.startswith("ibis_cache")]
    second_tables = [
        t for t in tables_after_second_caching if t.startswith("ibis_cache")
    ]

    assert sorted(first_tables) == sorted(second_tables)
