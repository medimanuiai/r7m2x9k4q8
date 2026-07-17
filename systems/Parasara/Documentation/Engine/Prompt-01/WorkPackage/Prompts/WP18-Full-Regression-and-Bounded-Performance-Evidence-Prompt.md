Execute **WP18 — full regression and bounded performance comparison** for Prompt-01.

Do not merely review this specification. Run the complete acceptance matrix, capture reproducible evidence, and create the WP18 completion report. **Do not modify production/test behavior and do not proceed to WP19.**

## Objective

Establish one authoritative post-implementation evidence package proving that Prompt-01 through WP17:

- passes the complete repository test suite repeatedly in Python 3.14.6 and Python 3.11.9;
- collects identical tests in both lanes;
- preserves all approved snapshots, fixed artifacts, Career public output, Yoga output, typed tooling output, and rule content;
- satisfies the WP17 architecture, safety, serialization, cache, registry, and cross-process determinism gates;
- remains stable across fresh processes, explicit hash seeds, safe working directories, loader/Yoga order permutations, and cold/warm cache state;
- has a recorded bounded performance profile for representative Stage-01 scenarios, with methodology and uncertainty clearly stated.

WP18 must produce evidence, not implementation. No production source, tests, fixtures, snapshots, rules, dependencies, workflows, or public schemas are expected to change.

## Hard preflight gate

Before running acceptance commands:

1. Locate and read by exact filename:
   - the locked Prompt-01 decisions/execution plan;
   - `Prompt-01-Final-Audit-Consolidation.md`;
   - final WP00-R and WP01 reports;
   - WP02 through WP17 completion reports;
   - Audits 21, 22, and 23, plus any earlier audit referenced by the final regression matrix.
2. Require every predecessor through WP17 to record `VERDICT: COMPLETE` and WP17 to record `WP18_READY: YES`.
3. Record the full inherited dirty worktree and preserve it exactly. Do not restore, stage, clean, delete, regenerate, or overwrite unrelated content.
4. Verify both locked interpreters and record exact Python, pytest, PyYAML, and Pydantic versions.
5. Verify all commands can use unique temporary directories, disable bytecode/pytest cache writes, and avoid fixed artifact paths.
6. Hash every protected tracked artifact before validation, including the approved snapshot and any fixed snapshot/report artifact identified by WP00-R through WP17.

Expected inherited WP17 evidence is:

- 781 identical collected nodes;
- node-ID SHA-256 `0b3ae6acb231a374a50fdc21b4c78c270340657f6365a3823136b2b7f53b0f7a`;
- 779 passed and 2 optional skips in each repeated full run per lane;
- deterministic scenario manifest: 1,898 bytes including final LF, SHA-256 `01b53b093e62e328de7758ed543a2c8f3b06c3a97e0502d7e879730e8c10d256`;
- approved snapshot: 4,041 bytes, with the lowercase SHA-256 recorded below.

When reporting, normalize SHA-256 to lowercase. The expected approved digest is:

`da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`

Reproduce these values; do not edit expectations or tracked artifacts to obtain them.

If prerequisites fail, stop without implementation changes and report:

```text
VERDICT: BLOCKED
WP19_READY: NO
```

## Absolute no-change boundary

WP18 may create only:

- unique temporary outputs outside tracked/fixed paths;
- the final WP18 Markdown report.

Do not modify:

- production code;
- tests or test configuration;
- rule/YAML/table files;
- fixtures, snapshots, approved goldens, or tracked artifacts;
- dependencies or lock files;
- CI/workflows;
- architecture documentation or completion matrices;
- prompt specifications for WP19.

If any regression or performance concern appears, investigate with read-only diagnostics, record it, and return `VERDICT: BLOCKED`. Do not fix it inside WP18. A separate remediation package must be authorized.

## Phase 1 — protected artifact manifest

Create an in-report manifest of protected files before execution. At minimum include:

- approved Stage-01 snapshot;
- `tests/tmp_snapshot.json` if still tracked/present;
- fixed Career/Yoga characterization snapshots or golden fixture outputs;
- tracked rule trace/coverage/report artifacts identified by WP16/WP17;
- rule/YAML/table files covered by Prompt-01;
- dependency lock/input files established by WP00-R.

For each, record repository-relative path, size, lowercase SHA-256, and protection class. After all validation and performance commands, re-hash them and require exact equality.

Do not place temporary generated files inside protected directories when a unique external temporary directory is available.

## Phase 2 — authoritative dual-lane regression

Run the following independently in Python 3.14.6 and Python 3.11.9 with:

- `PYTHONDONTWRITEBYTECODE=1`;
- `PYTHONPATH=.`;
- `NDASTRO_USE_SRTM=0` where relevant;
- `-o addopts=`;
- `-p no:cacheprovider`;
- a unique `--basetemp` per invocation.

Required sequence per lane:

1. import/version smoke check;
2. collect-only and ordered node-ID capture;
3. focused WP17 enforcement suite;
4. WP02–WP17 typed contract/integration suite;
5. all `tests/rules`;
6. Yoga and Career characterization/integration suites;
7. WP16 typed tooling/coverage tests;
8. full repository suite, fresh run 1;
9. full repository suite, fresh run 2;
10. full repository suite, fresh run 3.

Three final full runs are required in WP18 because this is the acceptance evidence package. Do not run a parallel-to-serial fallback that can hide a concurrency-only failure. Use the repository's proven serial mode unless a separate explicit parallel run is performed and reported independently.

Record exact commands, elapsed wall time as non-contractual diagnostics, collected/passed/failed/skipped/xfailed/xpassed counts, and exit codes. Require identical ordered node IDs and node-ID SHA-256 between lanes.

## Phase 3 — deterministic and order matrix

Re-run the WP17 deterministic scenario harness without editing its manifest:

- twice per process;
- at least two fresh processes per lane;
- `PYTHONHASHSEED=1` and `8675309` per lane;
- two explicit safe working directories;
- cold/warm cache state where applicable;
- unique artifact directory per process.

Require exact manifest bytes/hash and every per-scenario hash to equal WP17.

Also run and record:

- Yoga normal, reverse, A, B, and C explicit permutations;
- generic-loader then Yoga-loader;
- Yoga-loader then generic-loader;
- repeated isolated-registry construction;
- bounded cache fill/eviction/re-evaluation;
- Career fixed repeated projection;
- tooling artifact and coverage generation to unique paths.

No randomized test-order plugin or uncontrolled shuffle is permitted.

## Phase 4 — rule lint and snapshot acceptance

In each lane:

1. Run rule lint and prove every supported `.yml` and `.yaml` file is inspected exactly once.
2. Record the exact five expected files unless the repository inventory has legitimately changed before WP18; any unexplained difference blocks completion.
3. Run strict approved-snapshot comparison three times using a unique temporary output each time.
4. Never use update/approve mode.
5. Record generated and approved sizes/hashes and exact comparison result.
6. Verify temporary outputs are outside tracked/fixed paths and removed or left only inside the disposable temporary workspace.

Any snapshot difference is a regression to investigate, not an invitation to update the golden.

## Phase 5 — exact compatibility hash matrix

Reproduce and record exact bytes/hashes for:

- all three WP15/WP17 Career public fixtures;
- Yoga logical, full, and unchanged public projection;
- Yoga permutation aggregate;
- Career public aggregate;
- prepared predicate state and representative predicate logical/full results;
- recursive condition logical/full result;
- WP16 `rule_traces.json` projection;
- WP16 `career_rule_traces.json` projection;
- WP16 coverage JSON;
- WP17 deterministic scenario manifest and all ten scenario rows;
- approved snapshot and other protected tracked artifacts.

Require cold/warm, repeated, fresh-process, and cross-version byte equality wherever WP17 defines it. Telemetry-bearing full results may differ only in fields explicitly excluded from logical identity; record that distinction rather than comparing unstable timing values as contractual bytes.

## Phase 6 — bounded performance protocol

Performance measurement must be safe, deterministic in workload, non-mutating, and honest about environmental noise.

### Workloads

Measure these representative operations separately:

1. prepare predicate state from a fixed normalized fixture;
2. evaluate each canonical registered predicate once cold;
3. evaluate the same predicates warm through the bounded cache;
4. evaluate a representative nested condition cold and warm;
5. evaluate the fixed Yoga typed batch;
6. project Yoga public compatibility output;
7. prepare and evaluate each of the three fixed Career fixtures;
8. project each Career public output;
9. build the WP16 typed tooling/coverage projections in memory;
10. build the WP17 deterministic manifest once, excluding subprocess startup from engine-operation results;
11. strict logical serialization and SHA-256 for representative predicate, condition, Yoga, and Career results.

Do not benchmark file writes, dependency imports, environment creation, pytest startup, snapshot approval, network, raw Surya computation, or unrelated domains as predicate-engine performance.

### Measurement method

For each Python lane and workload:

- perform fixed untimed warm-up iterations;
- run at least 7 independent samples;
- each sample executes enough inner iterations to avoid timer-resolution noise while keeping total WP18 runtime bounded;
- use monotonic high-resolution timing only in the benchmark harness;
- clear/recreate evaluator/cache explicitly for cold samples;
- prebuild immutable fixtures outside the measured section unless preparation is the operation being measured;
- ensure outputs are consumed and their logical hash verified so work cannot be skipped;
- record sample count, iterations/sample, median, minimum, maximum, and median absolute deviation;
- report microseconds or milliseconds per operation as appropriate;
- run workloads in the same explicit order in both lanes;
- record host/OS/CPU information available without network access, while avoiding user paths or sensitive environment data.

Store raw samples only in the WP18 report or a temporary file summarized into the report. Do not add a permanent benchmark framework or dependency.

### Comparison policy

Use the following evidence hierarchy:

1. If an approved pre-Prompt-01 benchmark with identical workload/method/environment exists, compare medians and distributions directly.
2. Otherwise, explicitly state that no valid historical performance baseline exists. Use Python 3.11 versus 3.14 and repeated-run stability as a **descriptive comparison**, not proof of improvement or regression.
3. Compare cold versus warm only to demonstrate cache behavior, not as a migration before/after claim.
4. Do not invent a pass/fail percentage threshold after observing results.
5. Do not compare pytest wall time as an engine microbenchmark.

Without an approved identical historical baseline, performance completion means:

- every workload completes successfully;
- output hashes remain correct;
- no unbounded growth, runaway time, cache-capacity violation, or order-dependent result occurs;
- measurements and variability are recorded transparently;
- no unsupported “faster,” “slower,” or “no regression” claim is made.

If an operation shows extreme instability, unbounded growth, or a material anomaly that cannot be explained through read-only diagnostics, block WP18 and recommend a separately authorized remediation/benchmark investigation.

## Phase 7 — repository hygiene and final comparison

After all commands:

1. Re-hash every protected file and require exact pre/post equality.
2. Compare final `git status --short` with the captured starting state.
3. The only new intended tracked/untracked deliverable is the WP18 report.
4. Run `git diff --check`; distinguish inherited line-ending warnings from new errors.
5. Verify no bytecode, pytest cache, fixed artifact, root `-`, or generated snapshot was introduced by WP18.
6. Verify no production/test/rule/dependency/workflow file changed.

## Required WP18 report

Create:

`systems/Parasara/Documentation/Engine/Prompt-01/WorkPackage/Reports/WP18/WP18.md`

The report must include:

1. `VERDICT: COMPLETE` or `VERDICT: BLOCKED`;
2. `WP19_READY: YES` or `WP19_READY: NO`;
3. model and reasoning level used;
4. exact prerequisites and inherited worktree state;
5. environment/interpreter/dependency versions;
6. protected artifact pre/post manifest;
7. exact dual-lane commands, exit codes, counts, skips, node IDs/hash, and three full-run results;
8. focused contract/architecture/integration results;
9. subprocess/hash-seed/CWD/cold-warm determinism evidence;
10. Yoga permutation and loader-order evidence;
11. rule-lint inspected-file evidence;
12. three no-update snapshot comparisons per lane;
13. full logical/public/artifact compatibility hash matrix;
14. performance hardware/method/workload/sample disclosure;
15. raw performance summary by lane: iterations, samples, median, min, max, MAD, and unit;
16. any valid historical comparison, or explicit statement that none exists;
17. bounded performance interpretation with no unsupported claims;
18. final repository hygiene and protected-file equality;
19. changed-file inventory showing only this report;
20. blockers/anomalies, if any;
21. deferred WP19 and future-stage work;
22. explicit proof WP19 was not started.

## Definition of done

WP18 is complete only when:

- WP17 remains complete and reproducible;
- both Python lanes collect identical nodes;
- all focused and full suites pass, including three fresh full runs per lane;
- every WP17 deterministic scenario reproduces exact bytes/hashes across processes, hash seeds, CWDs, cache state, and Python lanes;
- Yoga permutations, loader orders, registry/cache isolation, and tooling projections pass;
- rule lint inspects every supported rule file exactly once;
- every strict snapshot comparison passes without update mode;
- all Career/Yoga/logical/public/tooling/protected hashes remain exact;
- the bounded performance protocol completes with correct outputs and transparent variability;
- no unsupported historical performance claim or invented threshold is used;
- protected files and the inherited worktree remain unchanged except for the WP18 report;
- the report records `VERDICT: COMPLETE` and `WP19_READY: YES`.

At the end, return a concise summary with verdict, model/reasoning, dual-lane counts, repeated full-run results, determinism and compatibility hashes, lint/snapshot status, bounded performance findings and limitations, repository hygiene, changed files, and WP19 readiness. **Do not proceed to WP19.**