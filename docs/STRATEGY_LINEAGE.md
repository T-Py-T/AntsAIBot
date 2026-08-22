# Strategy lineage and evidence boundary

This repository separates three algorithmic policies from a future learned
policy track. The separation matters: a runnable historical baseline is useful
evaluation infrastructure, but inherited strategy code is not original project
authorship and a local regression opponent is not automatically equivalent to
the competition winner it references.

## Policy inventory

| Policy | Repository entry point | Lineage | Current role |
| --- | --- | --- | --- |
| `AdvancedBot` | `src/bots/bot.py` | Replaced the initial bot in commit `ec7515f` and was subsequently maintained in this repository | Current default algorithmic policy |
| `InfluenceBot` / `IForOneWelcomeOurNewInsectOverlords` | `src/bots/influence_bot.py` | Exact strategy recovered from initial commit `fd85c05`; original header credits Tim Whitson | Attributed influence-map baseline, adapted to the current protocol and covered by characterization tests |
| Partial `XathisBot` | `src/bots/xathis_bot.py` | Repository-owned partial Python reimplementation of the preserved historical Java source | Regression opponent only; not strategically equivalent to the winner |
| Historical Xathis Java source | `docs/reference/xathis/` | Preserved first-place reference implementation | Fidelity target for a future executable Java comparison |

The recovered source depended on tuple-shaped movement helpers, a vision matrix,
and a setup callback that the current bot protocol does not provide. Its adapter
computes the same toroidal vision circle locally, translates tuple calls to the
current helper API, initializes lazily on the first turn, and annotates a copy
of the runtime map so strategy markers cannot corrupt protocol state. Food,
stale-visibility, combat, hill-defense, wave, and order-selection logic remain
the historical algorithm.

## What must be measured before changing the default

`InfluenceBot` is recovered, not crowned. A default-policy decision requires a
frozen comparison across multiple seeds and maps with, at minimum:

1. engine errors and timeouts;
2. wins, losses, draws, and score differential;
3. food gathered and colony growth over time;
4. explored-map coverage over time;
5. ant survival and hill outcomes; and
6. exact code revision, map, opponent revision, seeds, turn cap, and replays.

`make test-influence-vs-current` and `make test-influence-vs-xathis` provide
single-match diagnostics. `make benchmark-influence` provides repeated local
matchups. Results against `src/bots/xathis_bot.py` characterize a partial port,
not the historical leaderboard winner. A claim about matching or beating the
winner requires executing the preserved Java bot or a validated faithful port.

## Algorithmic baseline versus reinforcement learning

The algorithmic policies are deterministic, inspectable baselines. The future
RL track should remain a separate entry point and artifact family:

- train several model/policy variants from explicit observations, actions, and
  episodic outcomes;
- freeze maps, opponents, seeds, budgets, and scoring before comparison;
- retain checkpoints, configuration, learning curves, raw match results, and
  replays;
- compare learned policies against both algorithmic baselines; and
- promote a model only when held-out results support the claim.

Until that evidence exists, the repository demonstrates a local game-agent
evaluation platform and multiple algorithmic baselines—not a trained RL agent.
