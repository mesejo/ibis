from __future__ import annotations

import pytest

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
