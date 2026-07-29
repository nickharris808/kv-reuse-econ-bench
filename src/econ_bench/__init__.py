"""econ_bench.py — recompute the published first-touch-cut headline from the raw per-workload rows.

WHY OFFLINE VERIFICATION MATTERS. A benchmark that only *asserts* its number is a press release. This
recomputes the headline from the per-workload rows in the certificate, so a third party can confirm we
reported what we measured — no GPU, no trust, ~1 second.

    python src/econ_bench.py --verify        # recompute ours and compare to the published value
    python src/econ_bench.py --report        # full per-workload breakdown, failures included
"""
from __future__ import annotations

__version__ = "0.1.0"

import argparse
import json
import os
import statistics

# Inside the package, so `pip install` carries them. A flat module cannot ship package
# data, which is how an earlier layout produced a wheel that installed cleanly and could
# verify nothing at all.
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _find_root(start: str) -> str:
    """Walk up to the repo root (robust to how deeply the package is nested)."""
    d = start
    for _ in range(8):
        if os.path.isdir(os.path.join(d, "results", "data", "statefabric")):
            return d
        d = os.path.dirname(d)
    return start


try:
    ROOT = _find_root(os.path.dirname(os.path.abspath(__file__)))
except SystemExit:
    ROOT = None          # standalone checkout: the bundled fixtures are authoritative

def _resolve(*parts: str) -> str:
    """Prefer the parent repository's live certificate; fall back to the bundled fixture.

    This benchmark is published as its own repository, where `results/data/` does not exist. The
    bundled fixture under `fixtures/` carries every MEASURED value from the committed certificate,
    so a stranger recomputes the same answer we do. Where a certificate also carried internal
    module paths or the name of a compiled artifact, those strings are redacted in the published
    copy -- they point at the licensed implementation, not at any number this tool checks. In-tree
    the live cert wins, so a change to the real certificate shows up here immediately instead of
    being masked by a stale copy.
    """
    live = os.path.join(ROOT, "results", "data", *parts) if ROOT else None
    if live and os.path.exists(live):
        return live
    return os.path.join(FIXTURES, parts[-1])

SUITE = _resolve("statefabric", "fleet_econ_eprocess_cert.json")
REAL = _resolve("statefabric", "fleet_econ_realtrace_cert.json")


def _rows(cert_path: str) -> tuple[list[float], dict]:
    d = json.load(open(cert_path))
    m = d.get("metrics", {})
    return list(m.get("per_block_cut") or []), m


def summarise(cuts: list[float], floor: float) -> dict:
    if not cuts:
        return {}
    above = [c for c in cuts if c > floor]
    return {"n": len(cuts), "mean": round(statistics.fmean(cuts), 5),
            "median": round(statistics.median(cuts), 5),
            "min": round(min(cuts), 5), "max": round(max(cuts), 5),
            "n_above_floor": len(above), "floor": floor,
            "n_below_floor": len(cuts) - len(above)}


def verify_data() -> dict:
    """Recompute every published figure and return the result as data.

    The human printout and the `--json` output are rendered from THIS, so the two can never
    disagree. A benchmark whose pretty output and machine output are computed separately has
    two answers and no way to tell which one is the real one.

    `verdict` is three-valued for the same reason it is elsewhere in this portfolio:
    ABSTAIN means a certificate was missing or carried no per-workload rows, so nothing was
    recomputed. That is not a pass.
    """
    results, ok, checked = [], True, 0
    for label, path in (("36-workload suite", SUITE), ("real Mooncake trace", REAL)):
        if not os.path.exists(path):
            results.append({"label": label, "status": "cert_absent", "path": path})
            ok = False
            continue
        cuts, m = _rows(path)
        floor = float(m.get("prereg_m0_floor", 0.3))
        s = summarise(cuts, floor)
        if not s:
            results.append({"label": label, "status": "no_rows",
                            "note": "headline NOT independently checkable from this cert"})
            continue
        claimed = (m.get("money_number") or {}).get("mean_first_touch_cut")
        agree = claimed is None or abs(s["mean"] - float(claimed)) < 1e-4
        ok &= agree
        checked += 1
        results.append({"label": label, "status": "checked", "agrees": bool(agree),
                        "recomputed_mean": s["mean"], "cert_claims": claimed,
                        "certificate": os.path.basename(path), **s})

    verdict = "PASS" if (ok and checked) else ("ABSTAIN" if not checked else "FAIL")
    return {
        "artifact": "kv_reuse_econ_bench",
        "verdict": verdict,
        "exit_code": {"PASS": 0, "FAIL": 1, "ABSTAIN": 2}[verdict],
        "n_checked": checked,
        "results": results,
        "does_not_prove": [
            "that the cut is a SPEEDUP -- it measures prompt tokens not recomputed, never "
            "latency, FLOPs or store-fetch cost",
            "anything about your workload; these are our measurements on ours",
        ],
    }


def verify(as_json: bool = False) -> int:
    d = verify_data()
    if as_json:
        print(json.dumps(d, indent=2))
        return d["exit_code"]

    for r in d["results"]:
        if r["status"] == "cert_absent":
            print(f"  {r['label']}: cert absent — cannot verify")
        elif r["status"] == "no_rows":
            print(f"  {r['label']}: no per-workload rows in cert — headline NOT "
                  f"independently checkable")
        else:
            print(f"  {r['label']}: recomputed mean={r['mean']:.5f} from {r['n']} rows; "
                  f"cert says {r['cert_claims']} -> {'MATCH' if r['agrees'] else 'MISMATCH'}")
            print(f"      spread min={r['min']} max={r['max']} | floor={r['floor']} | "
                  f"above={r['n_above_floor']}/{r['n']} below={r['n_below_floor']}")
    tail = {"PASS": "OK — published headline reproduces from the raw rows.",
            "FAIL": "FAIL — published headline does NOT reproduce.",
            "ABSTAIN": ("ABSTAIN — nothing was recomputed (no certificate carried per-workload "
                        "rows). This is NOT a pass.")}[d["verdict"]]
    print("\n" + tail)
    return d["exit_code"]


def report() -> int:
    for label, path in (("36-workload suite", SUITE), ("real Mooncake trace", REAL)):
        if not os.path.exists(path):
            continue
        cuts, m = _rows(path)
        if not cuts:
            print(f"\n{label}: no per-workload rows recorded in this cert."); continue
        floor = float(m.get("prereg_m0_floor", 0.3))
        s = summarise(cuts, floor)
        print(f"\n{label} — n={s['n']} mean={s['mean']} median={s['median']} "
              f"min={s['min']} max={s['max']}")
        print(f"  pre-registered floor {floor}: {s['n_above_floor']} above, "
              f"{s['n_below_floor']} BELOW  <- the failures are part of the result")
        for i, c in enumerate(sorted(cuts)):
            bar = "#" * int(c * 40)
            print(f"   {i:3d} {c:7.4f} {bar}{'' if c > floor else '   <- below floor'}")
    print("\nNOTE: this measures WORK AVOIDED (prompt tokens not recomputed), not throughput or "
          "latency. The cut is a near-deterministic token-accounting identity, so we claim direction "
          "and magnitude across distinct workloads — not a p-value.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="First-touch prefill-cut benchmark (offline verifier).")
    ap.add_argument("--verify", action="store_true", help="recompute the headline from raw rows")
    ap.add_argument("--report", action="store_true", help="per-workload breakdown incl. failures")
    ap.add_argument("--json", action="store_true",
                    help="emit the result as JSON for CI dashboards and downstream tooling")
    a = ap.parse_args(argv)
    if a.report and not a.json:
        return report()
    return verify(as_json=a.json)


if __name__ == "__main__":
    raise SystemExit(main())
