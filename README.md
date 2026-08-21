# Ants Strategy Agent

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
| Strong reference opponent | [`src/bots/xathis_bot.py`](src/bots/xathis_bot.py), [`docs/reference/xathis/`](docs/reference/xathis) | Tested Python port anchored to preserved historical source |

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

[`statistics.json`](statistics.json) and
[`parallel_statistics.json`](parallel_statistics.json) are retained historical
runs, not a current leaderboard. They were produced at different times and do
not establish a general win-rate claim. A publishable comparison should record
the code revision, map set, seeds, turn limit, opponent revision, raw results,
and aggregation command in the same evidence bundle.

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
├── bots/               # strategy bot and Xathis reference port
├── sample_bots/        # fixed evaluation opponents in several languages
└── tools/              # match runner and map generation
tests/                  # deterministic regression suite
scripts/                # benchmark and analysis entry points
visualizer/             # replay viewer
maps/                   # retained evaluation maps
docs/reference/xathis/  # preserved historical reference source
```

## Scope and provenance

Taylor's work is the strategy implementation, Python reference port,
integration hardening, tests, benchmark/analysis tooling, and developer
workflow around the challenge. The repository also preserves challenge-engine,
sample-opponent, visualizer, and historical Xathis reference material so the
system can be exercised locally. Those retained components are reference and
compatibility inputs, not presented as original work; see
[`docs/gitroll-triage.md`](docs/gitroll-triage.md) for the explicit maintenance
boundary.

The repository does not currently publish a repository-wide license file.
Third-party source remains subject to its original terms and retained notices.
