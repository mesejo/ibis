from __future__ import annotations

import pytest

import ibis
from ibis.backends.datafusion.tests.conftest import BackendTest

pytest.importorskip("datafusion")


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
    # cleanup
    for table in tables_after_executing:
        if table.startswith("ibis_cache"):
            con.drop_table(table)


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
    # cleanup
    for table in first_tables:
        con.drop_table(table)


def test_cache_to_sql(con, alltypes):
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

    assert ibis.to_sql(cached) == ibis.to_sql(expr)


def test_op_after_cache(con, alltypes):
    expr = alltypes.select(
        alltypes.smallint_col, alltypes.int_col, alltypes.float_col
    )
    cached = expr.cache()
    cached = cached.filter(
        [
            cached.float_col > 0,
            cached.smallint_col == 9,
            cached.int_col < cached.float_col * 2,
        ]
    )

    full_expr = expr.filter(
        [
            alltypes.float_col > 0,
            alltypes.smallint_col == 9,
            alltypes.int_col < alltypes.float_col * 2,
        ]
    )

    actual = cached.execute()
    expected = full_expr.execute()

    BackendTest.assert_frame_equal(actual, expected)
    # the compile still works but is different from full_expr
    assert "functional_alltypes" in str(ibis.to_sql(cached))
    assert "ibis_cache" not in str(ibis.to_sql(expr))


