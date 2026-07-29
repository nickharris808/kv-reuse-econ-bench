import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import econ_bench

def test_published_headline_reproduces_from_raw_rows():
    """If our own reported mean does not recompute from the rows, we misreported."""
    assert econ_bench.verify() == 0

def test_failures_are_counted_not_hidden():
    cuts, m = econ_bench._rows(econ_bench.SUITE)
    s = econ_bench.summarise(cuts, float(m.get("prereg_m0_floor", 0.3)))
    assert s["n_above_floor"] + s["n_below_floor"] == s["n"]

def test_spread_is_reported_not_just_the_mean():
    cuts, m = econ_bench._rows(econ_bench.SUITE)
    s = econ_bench.summarise(cuts, 0.3)
    assert s["min"] < s["mean"] < s["max"], "a mean without a spread hides the weak workloads"
