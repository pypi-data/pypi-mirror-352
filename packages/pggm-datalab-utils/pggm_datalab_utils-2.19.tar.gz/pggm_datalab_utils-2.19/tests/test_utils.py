from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal

from dateutil.parser import parse as dateutil_parse
import math
from typing import Iterable, Optional

from pggm_datalab_utils.db import Record
from sql_keywords import SQL_KEYWORDS
from hypothesis import strategies as st, assume


def none_nan_to_zero(x: Optional[float]) -> float:
    return 0 if x is None or math.isnan(x) else x


def equivalent(x, y, sort_key=None):
    """Compares two json-ish objects to see if they are equal by value. Floats are equal if within 1e-5"""
    if x is None or y is None:
        pass
    if isinstance(x, Mapping) and isinstance(y, Mapping):
        assert all(isinstance(k, str) for k in x.keys() | y.keys()), 'non-string dict keys not supported'
        assert (all(k == k_ for k, k_ in zip(sorted(x.keys()), sorted(y.keys())))
                and all(equivalent(x[k], y[k], sort_key=sort_key) for k in x.keys()))
    elif isinstance(x, Iterable) and isinstance(y, Iterable) and not isinstance(x, str) and not isinstance(y, str):
        if sort_key is not None:
            x = sorted(x, key=sort_key)
            y = sorted(y, key=sort_key)
        assert all(equivalent(r_one, r_two, sort_key=sort_key) for r_one, r_two in zip(x, y))
    elif isinstance(x, datetime) and isinstance(y, str):
        assert x == dateutil_parse(y)
    elif isinstance(x, str) and isinstance(y, datetime):
        assert dateutil_parse(x) == y
    elif (isinstance(x, Decimal) and isinstance(y, Decimal)
          or isinstance(x, float) and isinstance(y, Decimal)
          or isinstance(x, Decimal) and isinstance(y, float)
          or isinstance(x, float) and isinstance(y, float)
    ):
        assert math.isnan(float(x)) and math.isnan(float(y)) or math.isclose(float(x), float(y), abs_tol=1e-5)
    else:
        assert (x == y or (x is None and y is None)
                or (isinstance(x, float) and math.isnan(x) and y is None)
                or (x is None and isinstance(y, float) and math.isnan(y))
                or (isinstance(x, float) and math.isnan(x) and isinstance(y, float) and math.isnan(y)))
    return True


any_data = st.one_of(st.text(), st.floats(), st.integers(), st.just(None), st.datetimes(), st.lists(st.integers()))
records = st.dictionaries(st.text(), any_data)


@st.composite
def pyframe_data(draw, min_size=1, max_size=None, min_width=1):
    keys = draw(st.lists(st.text(), min_size=min_width, unique=True))
    return draw(st.lists(st.fixed_dictionaries({k: any_data for k in keys}), min_size=min_size, max_size=max_size))


def nullable(strategy):
    return st.one_of(st.just(None), strategy)


@st.composite
def sql_friendly_indexed_data(draw, min_size=1, max_size=None):
    keys = draw(st.lists(st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1), min_size=2, unique=True))
    assume(not any(keyword.lower() in keys for keyword in SQL_KEYWORDS))

    data_options = [st.text(min_size=1), st.floats(allow_nan=False),
                    st.integers(min_value=-2 ** 32 + 1, max_value=2 ** 32 - 1), st.datetimes(), st.lists(st.integers())]
    hashable_options = [st.text(min_size=1), st.floats(allow_nan=False),
                        st.integers(min_value=-2 ** 32 + 1, max_value=2 ** 32 - 1)]

    idx = draw(st.lists(elements=st.sampled_from(keys), unique=True, min_size=1, max_size=len(keys) - 1))

    pf_data = {}
    pf_len = None
    for key in keys:
        if key in idx:
            strategy = draw(st.sampled_from(hashable_options))
            pf_data[key] = draw(
                st.lists(strategy, min_size=pf_len or min_size, max_size=pf_len or max_size, unique=True)
            )
        else:
            strategy = nullable(draw(st.sampled_from(data_options)))
            pf_data[key] = draw(
                st.lists(strategy, min_size=pf_len or min_size, max_size=pf_len or max_size)
            )
            assume(any(v is not None for v in pf_data[key]))
        pf_len = len(pf_data[key])

    pf_data = [dict(zip(pf_data.keys(), r)) for r in zip(*pf_data.values())]

    # Validate index draw
    if len(idx) == 1:
        ipf_data = {r[idx[0]]: r for r in pf_data}
    else:
        ipf_data = {tuple(r[i] for i in idx): r for r in pf_data}
    return ipf_data, idx


def sort_by_keys(data: list[Record], key: tuple) -> list[Record]:
    """
    Sort a list of records by some keys.
    """
    return sorted(data, key=lambda r: tuple(r[k] for k in key))


def test_lre_db():
    from pggm_datalab_utils.db import get_db_connection
    conn = get_db_connection('pggm-sql-lre-o.database.windows.net', 'lre')
    conn.close()
