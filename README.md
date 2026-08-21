# ants-strategy-agent

A deterministic multi-agent strategy system for the 2011 Ants AI Challenge,
packaged with a local game engine, reference opponents, replay visualization,
benchmark tooling, and PR-gated tests.

The engineering focus is the evaluation loop around the bot: run repeatable
matches, inspect replays, compare strategies against fixed opponents, and keep
the engine/protocol boundary covered by tests.

## At a glance

| Area | Public evidence | Signal |
| --- | --- | --- |
| Strategy implementation | [`src/bots/bot.py`](src/bots/bot.py) | Hierarchical objectives, persistent orders, collision avoidance, exploration, and combat heuristics |
| Game runtime | [`src/ants/`](src/ants), [`src/tools/playgame.py`](src/tools/playgame.py) | Local engine, sandboxing, protocol parsing, and match orchestration |
| Evaluation | [`Makefile`](Makefile), [`scripts/benchmark.py`](scripts/benchmark.py) | Named head-to-head, probabilistic, and benchmark entry points |
| Regression protection | [`tests/`](tests), [PR workflow](.github/workflows/ci.yml) | Unit, protocol, engine, sample-bot, Docker, and real-game checks |
| Qualitative debugging | [`visualizer/`](visualizer) | Browser replay inspection for behavior and failure analysis |
| Historical comparison | [`src/bots/xathis_bot.py`](src/bots/xathis_bot.py), [`docs/reference/xathis/`](docs/reference/xathis) | Partial Python reimplementation beside the preserved winning Java source |

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

This is a rule-based game agent, not a trained language model or reinforcement-
learning policy. The repository does include a reward-design analysis for a
possible learned successor, but that document is a design exercise rather than
implemented RL behavior.

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
make visualize-latest
```

Optional dependency groups are explicit so a contributor can install only the
surface being exercised:

| Extra | Contents | Use |
| --- | --- | --- |
| `[test]` | pytest and coverage support | Unit and integration regression checks |
| `[analysis]` | pandas, NumPy, SciPy, Matplotlib, and Seaborn | Benchmark aggregation and plots |
| `[dev]` | Both groups | Complete contributor environment |

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
├── bots/               # strategy bot and partial Xathis reimplementation
├── sample_bots/        # fixed evaluation opponents in several languages
└── tools/              # match runner and map generation
tests/                  # deterministic regression suite
scripts/                # benchmark and analysis entry points
visualizer/             # replay viewer
maps/                   # retained evaluation maps
docs/reference/xathis/  # preserved historical reference source
```

## Scope and provenance

Taylor's work includes the strategy implementation, partial Python Xathis
reimplementation, integration hardening, tests, benchmark/analysis tooling,
and developer workflow around the challenge. The repository also preserves
challenge-engine, sample-opponent, visualizer, and historical Xathis reference
material so the system can be exercised locally. Those retained components are
reference and compatibility inputs, not presented as original work; see
[`docs/gitroll-triage.md`](docs/gitroll-triage.md) for the explicit maintenance
boundary.

The preserved Java sources under `docs/reference/xathis/` are the historical
first-place Xathis bot. `src/bots/xathis_bot.py` is an incomplete Python
reimplementation: several strategy phases remain no-ops, and its combat search
is a simplified, bounded substitute for the original algorithm. Its tests show
that the implemented pieces and engine integration work; they do not establish
strategic fidelity or strength equivalent to the winning Java bot. Xathis
matchups in this repository are therefore regression and comparison inputs,
not evidence of world-class competitive performance.

The repository does not currently publish a repository-wide license file.
Third-party source remains subject to its original terms and retained notices.
