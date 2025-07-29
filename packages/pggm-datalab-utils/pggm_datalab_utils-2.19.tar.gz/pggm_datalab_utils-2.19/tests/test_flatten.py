from hypothesis import strategies as st, given
from pggm_datalab_utils.flatten import flatten_with_mapping, unflatten


@given(st.lists(elements=st.lists(elements=st.integers())))
def test_flatten_round_trip(it):
    assert unflatten(*flatten_with_mapping(it)) == it


@st.composite
def flattened_and_mappings(draw):
    mapping = draw(st.lists(st.integers(min_value=0, max_value=2 ** 8), unique=True, min_size=1, max_size=2 ** 8))
    flattened = draw(st.lists(st.integers(), min_size=sum(mapping), max_size=sum(mapping)))
    return flattened, mapping


@given(flattened_and_mappings())
def test_flatten_round_trip_vice_versa(f_and_m):
    assert flatten_with_mapping(unflatten(*f_and_m)) == f_and_m
