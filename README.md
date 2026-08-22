# ants-strategy-agent

A deterministic multi-agent strategy system for the 2011 Ants AI Challenge,
packaged with a local game engine, reference opponents, replay visualization,
benchmark tooling, and PR-gated tests.

The engineering focus is the evaluation loop around the bot: run repeatable
matches, inspect replays, compare strategies against fixed opponents, and keep
the engine/protocol boundary covered by tests.

**Current evidence boundary:** the public artifacts demonstrate a reproducible
game-agent evaluation platform, not a leaderboard-strength or reinforcement-
learning result. Competitive claims remain blocked until multi-map, multi-seed
matches against the executable historical Xathis bot support them.

![The retained deterministic replay rendered in the local visualizer, showing
four ant colonies, fog of war, score history, and turn controls. This image
demonstrates the replay path rather than a competitive result.](docs/assets/replay-current-evidence.png)

*Retained deterministic replay at turn 2/200. It demonstrates the working
map, fog-of-war, ant, score-history, and playback surfaces—not a win claim.*

## At a glance

| Area | Public evidence | Signal |
| --- | --- | --- |
| Strategy implementations | [`src/bots/bot.py`](src/bots/bot.py), [`src/bots/influence_bot.py`](src/bots/influence_bot.py) | Current hierarchical policy beside an attributed, recovered influence-map baseline |
| Game runtime | [`src/ants/`](src/ants), [`src/tools/playgame.py`](src/tools/playgame.py) | Local engine, sandboxing, protocol parsing, and match orchestration |
| Evaluation | [`Makefile`](Makefile), [`scripts/benchmark.py`](scripts/benchmark.py) | Named head-to-head, probabilistic, and benchmark entry points |
| Regression protection | [`tests/`](tests), [PR workflow](.github/workflows/ci.yml) | Unit, protocol, engine, sample-bot, Docker, and real-game checks |
| Qualitative debugging | [`visualizer/`](visualizer) | Browser replay inspection for behavior and failure analysis |
| Historical comparison | [`src/bots/xathis_bot.py`](src/bots/xathis_bot.py), [`docs/reference/xathis/`](docs/reference/xathis) | Partial Python reimplementation beside the preserved winning Java source |
| Provenance | [`docs/LICENSING.md`](docs/LICENSING.md), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) | Apache-2.0 project boundary with explicit historical-source exceptions |

## System design

```text
map + game state
       │
       ▼
priority policy
  1. continue valid standing orders
  2. protect colony growth
  3. target enemy hills
  4. collect food
  5. engage when advantageous
  6. explore unseen space
       │
       ▼
collision-safe orders ──► engine / sandbox ──► replay + result artifacts
                                      │
                                      └──────► benchmark aggregation
```

The diagram describes the current default `AdvancedBot`. The independently
invocable `InfluenceBot` uses propagated heat maps for food, fog-of-war edges,
combat safety, hill defense, and coordinated waves. Its historical class name
is `IForOneWelcomeOurNewInsectOverlords`; the descriptive alias makes its role
clear without erasing the source identity. See
[`docs/STRATEGY_LINEAGE.md`](docs/STRATEGY_LINEAGE.md) for the exact lineage,
attribution, and evaluation boundary.

The implemented bots are rule-based agents, not trained language models or
reinforcement-learning policies. Future RL work is a separate model track: it
will train policy variants from state/action/reward trajectories and evaluate
them against frozen algorithmic baselines. No model-performance claim is made
until those runs and their artifacts exist.

## Evaluation contract

The project supports three useful levels of evidence:

1. `make pytest` checks deterministic components and structural contracts.
2. `make test` runs a real 30-turn game through the local engine.
3. Benchmark targets run repeated matches against named reference opponents and
   emit machine-readable results for analysis.

```bash
make pytest
make test
make test-vs-xathis
make benchmark-xathis
make test-influence-vs-current
make test-influence-vs-xathis
make benchmark-influence
```

Reproducing an engine run requires two independent values. `engine_seed`
controls engine-side randomness such as food generation; `player_seed` is sent
to each bot so opponents with randomized policies can reproduce their choices.
The showcased Make targets default to `SEED=42`: game targets pass it as both
values, while the benchmark runner uses it as a recorded master seed from which
it derives and records an engine/player seed pair for every game. Override it
with a command such as `make benchmark SEED=73`. The same code revision, map,
arguments, bot revisions, and both per-game seeds are required for a repeatable
comparison. Wall-clock timeouts and runtime differences remain external
sources of variation.

[`statistics.json`](statistics.json) and
[`parallel_statistics.json`](parallel_statistics.json) are retained historical
runs, not a current leaderboard. They were produced at different times and do
not establish a general win-rate claim. A publishable comparison should record
the code revision, map set, seeds, turn limit, opponent revision, raw results,
and aggregation command in the same evidence bundle.

### Current retained evidence

[`results/current-evidence-v1/`](results/current-evidence-v1/) is the first
current-SHA packet. Its fixed 14-game workload completed with zero engine errors
and 14 draws: zero wins and zero losses. The value of this small packet is the
traceable benchmark-to-replay path, not strategic-performance evidence.

| Question | Exact artifact |
| --- | --- |
| What ran? | [`benchmarks/current-evidence-v1.json`](benchmarks/current-evidence-v1.json) |
| What happened in every game? | [`results/current-evidence-v1/deterministic-result.json`](results/current-evidence-v1/deterministic-result.json) |
| What did the runner emit? | [`results/current-evidence-v1/benchmark-raw.json`](results/current-evidence-v1/benchmark-raw.json) |
| Can I inspect a game? | [`results/current-evidence-v1/replay/four-player-final.replay`](results/current-evidence-v1/replay/four-player-final.replay) |
| Are the files intact? | [`results/current-evidence-v1/manifest.json`](results/current-evidence-v1/manifest.json) |
| What does it prove? | [`results/current-evidence-v1/README.md`](results/current-evidence-v1/README.md) |

The packet is tied to default-branch commit `69bc75d6e6bb26c5f68ca02432bf313aae4aa2b2`,
one master seed, two games per matchup, and a 200-turn cap. It is a deterministic
regression sample, not a statistically significant win-rate estimate or a
universal strategy claim.

## Local setup

The canonical environment uses [`uv`](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/T-Py-T/ants-strategy-agent.git
cd ants-strategy-agent
uv sync --all-extras

make pytest
make test
make visualize-evidence
```

`make visualize-evidence` opens the retained current-SHA replay with the map,
ants, score history, and turn controls. `make visualize-latest` instead opens
the newest replay produced under `game_logs/` during local development.

Install the local commit gate once with
`uv run --all-extras pre-commit install`. It runs a staged-diff check and the
full test suite before a commit is accepted. The hook requests all extras so a
fresh environment includes the benchmark-analysis imports exercised by tests.

Optional dependency groups are explicit so a contributor can install only the
surface being exercised:

| Extra | Contents | Use |
| --- | --- | --- |
| `[test]` | pytest and coverage support | Unit and integration regression checks |
| `[analysis]` | pandas, NumPy, SciPy, Matplotlib, and Seaborn | Benchmark aggregation and plots |
| `[dev]` | Both groups plus pre-commit | Complete contributor environment |

Docker and a VS Code dev container are available when a host-local Python/Java
toolchain is undesirable:

```bash
make docker-build
make docker-test
```

The hosted workflow is intentionally a pull-request merge gate. Routine branch
pushes do not consume GitHub Actions minutes; agents are expected to run the
same checks locally before opening or updating a PR.

## Project Structure

```
src/
├── ants/               # engine, game state, protocol, sandbox
├── bots/               # current policy, recovered baseline, partial Xathis
├── sample_bots/        # fixed evaluation opponents in several languages
└── tools/              # match runner and map generation
tests/                  # deterministic regression suite
scripts/                # benchmark and analysis entry points
visualizer/             # replay viewer
maps/                   # retained evaluation maps
docs/reference/xathis/  # preserved historical reference source
```

## Scope, licensing, and provenance

Taylor's work includes the current `AdvancedBot`, the Python integration around
a partial Xathis adaptation, integration hardening, tests, benchmark/analysis
tooling, and developer workflow around the challenge. `InfluenceBot` is a recovered,
attributed strategy originally written by Tim Whitson; Taylor's repository work
on it is the current-protocol adaptation, characterization, and comparative
evaluation—not authorship of the underlying algorithm. The repository also
preserves challenge-engine, sample-opponent, visualizer, and historical Xathis
reference material so the system can be exercised locally. Those retained
components are reference and compatibility inputs, not presented as original
work; see
[`docs/gitroll-triage.md`](docs/gitroll-triage.md) for the explicit maintenance
boundary.

The preserved Java sources under `docs/reference/xathis/` are the historical
first-place Xathis bot. `src/bots/xathis_bot.py` is an incomplete Python
reimplementation that directly adapts Xathis constants, data structures, phase
ordering, and methods: several strategy phases remain no-ops, and its combat
search is a simplified, bounded substitute for the original algorithm. Its
tests show that the implemented pieces and engine integration work; they do not
establish strategic fidelity or strength equivalent to the winning Java bot.
Xathis matchups in this repository are therefore regression and comparison
inputs, not evidence of world-class competitive performance.

Taylor's original contributions and the Apache-licensed AI Challenge-derived
infrastructure are available under the
[`Apache License 2.0`](LICENSE). The project license does not relicense two
attributed historical strategy lineages for which no license grant was located:
the unchanged Xathis Java snapshot, Xathis-derived portions of the Python
adaptation, and the original portions of Tim Whitson's influence-map bot. Those
portions remain under their authors' terms and are excluded from the project
grant; Taylor's independently authored integration work remains Apache-2.0.

Read [`docs/LICENSING.md`](docs/LICENSING.md) for the component inventory and
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for exact upstream revisions
and exceptions. Contributions follow [`CONTRIBUTING.md`](CONTRIBUTING.md), and
security reports follow [`SECURITY.md`](SECURITY.md).
