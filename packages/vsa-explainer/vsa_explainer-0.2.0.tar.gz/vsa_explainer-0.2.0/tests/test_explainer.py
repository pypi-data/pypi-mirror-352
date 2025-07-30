import pytest
from vsa_explainer import (
    load_crippen_data,
    get_vsa_bin_bounds,
    get_bin_bounds,
    visualize_vsa_contributions,
)

def test_load_crippen_data():
    data = load_crippen_data()
    assert isinstance(data, list)
    # each entry is a tuple of length 5
    assert all(len(t) == 5 for t in data)

@pytest.mark.parametrize("bins,idx,expected", [
    ([0.1, 0.5, 1.0], 1, (-float("inf"), 0.1)),
    ([0.1, 0.5, 1.0], 2, (0.1, 0.5)),
    ([0.1, 0.5, 1.0], 4, (1.0, float("inf"))),
])
def test_get_bin_bounds(bins, idx, expected):
    assert get_bin_bounds(idx, bins) == expected

def test_get_vsa_bin_bounds_smrvsa8():
    # SMR_VSA8 should parse from Descriptors.__doc__
    lb, ub = get_vsa_bin_bounds("SMR_VSA8")
    assert lb < ub  # sanity check

def test_visualize_vsa_contributions_smoke(capsys):
    # just ensure it runs without crashing on a simple molecule
    visualize_vsa_contributions("CCO", ["SMR_VSA1"])
    # it should print either contributions or “No atoms contribute…”:
    captured = capsys.readouterr()
    assert "SMR_VSA1" in captured.out
