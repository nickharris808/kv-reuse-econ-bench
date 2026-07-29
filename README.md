# kv-reuse-econ-bench

**We published a 90% cache-reuse headline. This tool proves it is arithmetic.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](pyproject.toml)

A standard measurement for **first-touch prefill cut** — the fraction of prompt tokens an engine
did *not* recompute because a prefix was already resident — that recomputes our own headline from
the raw rows and shows you exactly how much of it is a system property.

```bash
pip install kv-reuse-econ-bench
```

## Why this exists

Everyone quotes a cache-hit number. Nobody agrees on how it was measured, and almost nobody
publishes the per-workload spread that would let you check.

We published **90.0%**. Then we checked it against a closed form and found:

```
cut(n) = 256 · ⌊n/256⌋ / n
```

The chunk size over the prompt length. It reproduces to **five decimal places without the GPU
data**, moves to 0.947 on a different size ramp, and the pre-registered 0.30 floor was
unfalsifiable — any prompt ≥ 512 tokens clears it by construction.

So this benchmark ships the refutation as a feature. It recomputes the headline from the rows,
prints the whole distribution, and shows the failures rather than the mean.

## Provenance

Every figure here resolves through `oss/provenance.py` to a committed certificate:
the 90.0% suite mean to `results/data/statefabric/fleet_econ_eprocess_cert.json`
(registered as `first_touch_cut_suite`), the 0.668 real-trace mean to
`fleet_econ_realtrace_cert.json` (`first_touch_cut_realtrace`). Both are bundled under
`fixtures/`, so `--verify` recomputes them with no parent repository.

## Install

```bash
pip install kv-reuse-econ-bench     # zero dependencies; fixtures bundled
```

## 30-second quickstart

```bash
kv-reuse-econ-bench --verify        # does the published headline reproduce from the rows?
kv-reuse-econ-bench --report        # the full per-workload distribution, failures included
```

No GPU, no network, no parent repository — the certificates are bundled.

## Worked example

```console
$ kv-reuse-econ-bench --verify
  36-workload suite: recomputed mean=0.89976 from 36 rows; cert says 0.89976 -> MATCH
      spread min=0.54936 max=0.99805 | floor=0.3 | above=36/36 below=0
  real Mooncake trace: recomputed mean=0.66804 from 29 rows; cert says 0.66804 -> MATCH
      spread min=0.0 max=0.97959 | floor=0.3 | above=23/29 below=6

OK — published headline reproduces from the raw rows.
```

Read the second block. On the **real** Mooncake trace the mean is 0.668, the minimum is **0.0**,
and **6 of 29 workloads fall below the floor**. Those six are the honest part: real prompts often
have little or no reusable prefix, and a benchmark that reported only the mean would hide that.

## Measuring your own

The comparison that matters is not our number against yours — it is your number against the closed
form for **your** chunk size and prompt distribution. If they coincide, you have measured your
configuration, not your system.

## Honest limits

- **No latency, no FLOPs, no throughput.** These are token-accounting quantities. A prefill cut is
  not a speedup, and this tool will never print one.
- **The store-fetch cost is not netted out.** Fetching KV from a remote store is not free.
- **The synthetic headline is ramp-dependent** and the tool demonstrates that rather than asserting it.
- **`--verify` checks reproduction, not truth.** It proves the published number follows from the
  published rows. Whether those rows describe your workload is a separate question.

## The commercial edition

This benchmark **measures and reports**. The pooling fabric it characterises — cross-instance KV
reuse, the fleet controller, capsule logistics — is covered by filed claims and licensed separately.

**Reading is free. The fabric is the product.**

## Licence

Apache-2.0 · **CLEAN**.

**Third-party data:** the bundled `fleet_econ_realtrace_cert.json` fixture is derived from the
**Mooncake** trace — Apache-2.0, © kvcache-ai, <https://github.com/kvcache-ai/Mooncake>
(USENIX FAST '25). It holds per-workload accounting aggregates only, with no prompt or response
text. See [`NOTICE`](NOTICE).
Baseline result: [`results/baseline.json`](results/baseline.json).

<!-- HONEST-SCOPE -->
## Honest scope — what a passing run proves, and what it does not

The two halves are inseparable. A tool that states only the first half is marketing.

**It proves:**

- that our published first-touch-cut headline follows arithmetically from the raw per-workload rows in the certificate

**It does NOT prove:**

- that the cut is a SPEEDUP. It counts prompt tokens not recomputed — never latency, FLOPs, or store-fetch cost
- anything about your workload; these are our measurements on ours
- that the headline is interesting: it is close to the identity 256·⌊n/256⌋/n

Full CLI reference, generated from `--help`: [`docs/CLI.md`](docs/CLI.md)
<!-- /HONEST-SCOPE -->

## Contributing

Bug reports and pull requests welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

**A false accusation is a defect of equal severity to a missed detection.** If this tool flags something correct, open an issue with the input and the verdict you expected: over-refusal trains people to bypass refusals, which destroys the tool.

Citation metadata is in [CITATION.cff](CITATION.cff).

<!-- PORTFOLIO -->
---

## The rest of the portfolio

25 artifacts, one idea: **a measurement you cannot check is a press release.** Every tool
here reports; none of them gates.

**Tools**

| | |
|---|---|
| [`abstain-bench`](https://github.com/nickharris808/abstain-bench) | how often does a verifier pass input it could not check? |
| [`evidence`](https://github.com/nickharris808/evidence) | run the whole portfolio over your repo — the weakest leg, never the mean |
| [`floorgen`](https://github.com/nickharris808/floorgen) | what must your system remember? an exact lower bound |
| [`formal-proof-mcp`](https://github.com/nickharris808/formal-proof-mcp) | a proof kernel for your coding agent |
| [`gatecount`](https://github.com/nickharris808/gatecount) | exactly how many states does removing this check admit? |
| [`gridlock`](https://github.com/nickharris808/gridlock) | certify a wait-for relation cannot wedge |
| [`honestbench`](https://github.com/nickharris808/honestbench) | measure your CI's escape rate |
| [`kvleak`](https://github.com/nickharris808/kvleak) | cross-tenant leak scanner |
| [`kvprobe`](https://github.com/nickharris808/kvprobe) | model-substitution detector with a measured FPR |
| [`preregister`](https://github.com/nickharris808/preregister) | refuses to seal a plan whose conclusion is already fixed |
| [`proof-carrying-ci`](https://github.com/nickharris808/proof-carrying-ci) | the whole portfolio as one CI check, with SARIF |
| [`proof-to-code-drift`](https://github.com/nickharris808/proof-to-code-drift) | fail the build when the proof stops matching |
| [`sf-verify`](https://github.com/nickharris808/sf-verify) | re-derive admission decisions offline |
| [`signoff-cert`](https://github.com/nickharris808/signoff-cert) | certificates that carry their own false-pass bound |
| [`tokencount`](https://github.com/nickharris808/tokencount) | a token count both parties can recompute |

**Benchmarks** — each recomputes one of our own published numbers from its certificate

| | |
|---|---|
| [`illusion-bench`](https://github.com/nickharris808/illusion-bench) | how many broken kernels does your oracle admit? |
| [`kv-reuse-econ-bench`](https://github.com/nickharris808/kv-reuse-econ-bench) | recompute our economics headline ← you are here |
| [`llm-tenant-isolation-bench`](https://github.com/nickharris808/llm-tenant-isolation-bench) | recompute our isolation figures |

**Datasets**

| | |
|---|---|
| [`abstain-corpus`](https://huggingface.co/datasets/nickh007/abstain-corpus) | 32 inputs a verifier must NOT pass |
| [`kv-reuse-econ-traces`](https://huggingface.co/datasets/nickh007/kv-reuse-econ-traces) | per-workload reuse accounting + the closed form |
| [`kv-tenant-isolation-bench`](https://huggingface.co/datasets/nickh007/kv-tenant-isolation-bench) | isolation observations, uninterpretable rows included |
| [`llm-precision-fingerprints`](https://huggingface.co/datasets/nickh007/llm-precision-fingerprints) | precision-labelled logprobs with a negative control |

**Try it in a browser** — no install, no GPU

| | |
|---|---|
| [`negative-results-atlas`](https://huggingface.co/spaces/nickh007/negative-results-atlas) | ten claims we took back |
| [`tenant-leak-demo`](https://huggingface.co/spaces/nickh007/tenant-leak-demo) | the residency calculator |
| [`wait-for-visualiser`](https://huggingface.co/spaces/nickh007/wait-for-visualiser) | paste a wait-for graph, see the cycle |

### Documentation

Everything above, explained in one place: **<https://nickharris808.github.io/evidence-docs/>** —
the [tutorial](https://nickharris808.github.io/evidence-docs/start/tutorial/),
[what this proves and what it does not](https://nickharris808.github.io/evidence-docs/concepts/what-this-proves/),
and a [CLI reference](https://nickharris808.github.io/evidence-docs/reference/cli/) generated by
running `--help` on every published command.

### The commercial edition

Everything above is **measure-only** and Apache-2.0: it tells you what is true and never acts on
it. The **enforcement** side — binding a partition key at the admission decision, the compiled gate
corpus, and the certificate-*issuing* faucet — is covered by filed patents and licensed separately.

**Reading is free. Enforcing is licensed.**
<!-- /PORTFOLIO -->
