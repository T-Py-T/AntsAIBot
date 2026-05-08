#!/usr/bin/env python
"""XathisBot — a Python port of the AI Challenge 2011 winning bot.

The original is in ``docs/reference/xathis/Strategy.java`` (1,773 lines) and
the postmortem is at ``docs/reference/xathis/postmortem.txt``.

This is V1: scaffolding only. It puts the full data model in place
(``Tile`` / ``Ant`` / torus geometry / combat distances) and the empty
phase ladder from ``Strategy.actions()``. Every phase is a stub that
returns immediately; the bot falls back to a trivial "all ants stay
put" behaviour so it never crashes the engine.

Subsequent commits fill in one phase at a time, in this order:

    initTurn        bookkeeping, dangered/willStay flags, gammaDistEnemies
    food            multi-source BFS from food tiles
    enemyHills      BFS from enemy hills, send up to 4 attackers
    explore         exploreValue diffusion + 11-step BFS
    createAreas     territory flood-fill + border tiles
    fight           gamma-group minimax (the killer feature)
    defence         hill defender interception
    missions        long-running goals to border tiles
    escape          dangered-ant safe-tile lookahead

Each phase added is independently testable; the bot stays playable at
every step.

Reference: ``docs/reference/xathis/Strategy.java`` line numbers are cited
in the docstring of each ported method.
"""

from __future__ import annotations

import sys
import time
from typing import Dict, List, Optional, Set, Tuple

# Reuse the shared helper API for stdio + map state. Constants we use:
#   MY_ANT (0), LAND (-2), FOOD (-3), WATER (-4), UNSEEN (-5), HILL (-6)
#   AIM = {'n': (-1, 0), ...}
from ants import (  # type: ignore[import-not-found]
    AIM,
    ANTS,
    DEAD,
    FOOD,
    HILL,
    LAND,
    MY_ANT,
    UNSEEN,
    WATER,
    Ants,
)


# ---------------------------------------------------------------------------
# Tunable constants (lifted directly from Strategy.java)
# ---------------------------------------------------------------------------
# CLOSE_ENEMY_RADIUS — Strategy.java:21
CLOSE_ENEMY_RADIUS: int = 9
CLOSE_ENEMY_RADIUS2: int = CLOSE_ENEMY_RADIUS ** 2

# AREA_DIST — Strategy.java:23
AREA_DIST: int = 20

# Time budget per turn, in ms; xathis sets isTimeout at 420ms and the engine
# default turntime is 500ms. We keep the same headroom.
TURN_TIME_BUDGET_MS: int = 420

# Hill defence horizon — Strategy.java:389
DEFENCE_HORIZON: int = 14

# Food BFS horizon — Strategy.java:572
FOOD_BFS_HORIZON: int = 13

# Explore BFS horizon — Strategy.java:944
EXPLORE_BFS_HORIZON: int = 11

# Escape BFS horizon — Strategy.java:599
ESCAPE_CHECK_DIST: int = 8


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
class Tile:
    """A single map cell. Persisted across turns; mutable.

    Mirrors ``docs/reference/xathis/Tile.java``. Many fields are scratch
    space for various BFS passes; we reset them between phases via the
    standard ``isReached`` / ``changedTiles`` pattern.
    """

    __slots__ = (
        "row", "col", "tile_type",
        "ant", "old_ant",
        "neighbors",
        "is_hill", "hill_player",
        # bfs scratch (not reset between turns)
        "dist", "hill_dist", "prev",
        "is_reached",
        # food bfs
        "source",
        # explore
        "explore_value", "prev_firsts", "has_new_land",
        # A*
        "f",
        # distribute
        "is_reached_by_me",
        # combat simulation
        "has_virt_ant",
        # areas
        "start_tile", "is_in_my_area", "is_border",
        # willStay detection
        "stay_turn_count", "stay_value",
        # dep tables
        "is_checked",
    )

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.tile_type: int = LAND
        self.ant: Optional["Ant"] = None
        self.old_ant: Optional["Ant"] = None
        self.neighbors: Tuple["Tile", ...] = ()
        self.is_hill: bool = False
        self.hill_player: int = -1
        self.dist: int = 0
        self.hill_dist: int = 1 << 30
        self.prev: Optional["Tile"] = None
        self.is_reached: bool = False
        self.source: Optional["Tile"] = None
        self.explore_value: int = 100
        self.prev_firsts: Set["Tile"] = set()
        self.has_new_land: bool = False
        self.f: int = 0
        self.is_reached_by_me: bool = False
        self.has_virt_ant: bool = False
        self.start_tile: Optional["Tile"] = None
        self.is_in_my_area: bool = False
        self.is_border: bool = False
        self.stay_turn_count: int = 0
        self.stay_value: int = -1
        self.is_checked: bool = False

    def is_free(self) -> bool:
        """True if this tile is land (not water, food, ant, or hill).

        Mirrors ``Type.isFree()`` (Strategy.java references) — note that
        in the Java version 'free' means LAND specifically, and food /
        hills / ants are considered occupied.
        """
        return self.tile_type == LAND

    def is_enemy(self) -> bool:
        return self.tile_type > MY_ANT  # players 1..9

    def dir_to(self, other: "Tile") -> str:
        """Return the cardinal direction ('n'/'e'/'s'/'w') from this tile
        to a *direct* neighbor, accounting for torus wrap.

        Mirrors ``Tile.dirTo`` (Tile.java:55).
        """
        if other.row == self.row:
            if other.col == self.col + 1:
                return "e"
            if other.col == self.col - 1:
                return "w"
            # wrapped
            return "w" if self.col == 0 else "e"
        if other.row == self.row + 1:
            return "s"
        if other.row == self.row - 1:
            return "n"
        return "n" if self.row == 0 else "s"

    def __repr__(self) -> str:
        return f"Tile({self.row},{self.col})"


class Ant:
    """An ant; lives one turn. Mirrors ``docs/reference/xathis/Ant.java``."""

    __slots__ = (
        "tile",
        "is_dangered", "is_indirectly_dangered",
        "has_moved", "has_mission",
        "is_detached",
        "close_enemy_dists",     # list[(dist2, Ant)] sorted
        "closest_enemy_tile",
        "close_enemy_dists_sum",
        "closest_enemy",
        "closest_enemy_dist",
        "num_close_enemies",
        "gamma_dist_enemies",    # list[Ant]
        "is_dead", "weakness",
        "is_reached", "is_grouped", "is_gamma_grouped",
        "curr_to", "best_to",
        "comp_value",
        "mission",
        "num_close_own_ants",
        "will_stay",
        "dep_table",
        "check_all", "check_neighbors",
        "dist_map",
    )

    def __init__(self, tile: Tile) -> None:
        self.tile: Tile = tile
        self.is_dangered: bool = False
        self.is_indirectly_dangered: bool = False
        self.has_moved: bool = False
        self.has_mission: bool = False
        self.is_detached: bool = True
        self.close_enemy_dists: List[Tuple[int, "Ant"]] = []
        self.closest_enemy_tile: Optional[Tile] = None
        self.close_enemy_dists_sum: int = 0
        self.closest_enemy: Optional["Ant"] = None
        self.closest_enemy_dist: int = 1 << 30
        self.num_close_enemies: int = 0
        self.gamma_dist_enemies: List["Ant"] = []
        self.is_dead: bool = False
        self.weakness: int = 0
        self.is_reached: bool = False
        self.is_grouped: bool = False
        self.is_gamma_grouped: bool = False
        self.curr_to: Optional[Tile] = None
        self.best_to: Optional[Tile] = None
        self.comp_value: int = 0
        self.mission: Optional["Mission"] = None
        self.num_close_own_ants: int = 0
        self.will_stay: bool = False
        self.dep_table: Optional[Dict[Tile, List[Tile]]] = None
        self.check_all: bool = False
        self.check_neighbors: List[Tile] = []
        self.dist_map: Optional[Dict[Tile, int]] = None

    def __repr__(self) -> str:
        return f"Ant({self.tile.row},{self.tile.col})"


class Mission:
    """A long-running goal: an ant heading toward a target tile.

    Mirrors ``Strategy.Mission`` (Strategy.java:256). Persists across
    turns; the path is recomputed via A* every time.
    """

    __slots__ = ("target", "curr_tile", "last_updated", "is_removed")

    def __init__(self, target: Tile, curr_tile: Tile, turn: int) -> None:
        self.target: Tile = target
        self.curr_tile: Tile = curr_tile
        self.last_updated: int = turn
        self.is_removed: bool = False


# ---------------------------------------------------------------------------
# XathisBot
# ---------------------------------------------------------------------------
class XathisBot:
    """Faithful Python port of xathis's AI Challenge 2011 winning bot.

    Used as the "final boss" opponent for AdvancedBot and future
    ML-driven variants in this repo.

    The phase ladder in ``do_turn`` mirrors ``Strategy.actions()``
    (Strategy.java:203). Each phase is one method on this class; phases
    not yet implemented are no-ops that fall through.
    """

    def __init__(self) -> None:
        # Persistent state across turns. Tiles are created lazily on the
        # first do_turn (we need rows/cols from the engine).
        self.rows: int = 0
        self.cols: int = 0
        self.tiles: List[List[Tile]] = []
        self.turn: int = 0
        self.start_time_ms: float = 0.0
        self.is_timeout: bool = False

        # Per-turn data (rebuilt each turn from the engine state).
        self.my_ants: List[Ant] = []
        self.enemy_ants: List[Ant] = []
        self.foods: List[Tile] = []
        self.my_hills: List[Tile] = []
        self.enemy_hills: List[Tile] = []
        self.dangered_ants: List[Ant] = []

        # Long-running missions (persist across turns).
        self.missions: List[Mission] = []

    # ------------------------------------------------------------------
    # Initialization (called on first turn once we know map dimensions)
    # ------------------------------------------------------------------
    def _ensure_initialized(self, ants: Ants) -> None:
        if self.tiles:
            return
        self.rows = ants.height
        self.cols = ants.width
        self.tiles = [[Tile(r, c) for c in range(self.cols)] for r in range(self.rows)]
        # Precompute neighbors. We don't yet know which tiles are water
        # (UNSEEN starts everywhere); we'll prune water neighbors lazily
        # when we encounter them in update_map_state. For now every tile
        # has 4 cardinal neighbors with torus wrap.
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                tile.neighbors = (
                    self.tiles[(r - 1) % self.rows][c],   # n
                    self.tiles[r][(c + 1) % self.cols],   # e
                    self.tiles[(r + 1) % self.rows][c],   # s
                    self.tiles[r][(c - 1) % self.cols],   # w
                )

    def _prune_water_neighbors(self, ants: Ants) -> None:
        """Mark known-water tiles and prune them from neighbors lists.

        xathis treats water as a permanent edge in the navigation graph;
        the original ``Tile.removeNeighbor`` (Tile.java:67) is called
        once per tile when water is first observed.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                if ants.map[r][c] == WATER:
                    tile = self.tiles[r][c]
                    if tile.tile_type != WATER:
                        tile.tile_type = WATER
                        # Remove this tile from each of its (former) neighbors.
                        for n in tile.neighbors:
                            if tile in n.neighbors:
                                n.neighbors = tuple(x for x in n.neighbors if x is not tile)
                        tile.neighbors = ()

    # ------------------------------------------------------------------
    # Torus geometry
    # ------------------------------------------------------------------
    def dist_row(self, t1: Tile, t2: Tile) -> int:
        d = abs(t1.row - t2.row)
        return min(d, self.rows - d)

    def dist_col(self, t1: Tile, t2: Tile) -> int:
        d = abs(t1.col - t2.col)
        return min(d, self.cols - d)

    def dist(self, t1: Tile, t2: Tile) -> int:
        """Manhattan distance on the torus (Strategy.java:1752)."""
        return self.dist_row(t1, t2) + self.dist_col(t1, t2)

    # ------------------------------------------------------------------
    # Combat distances (alpha < beta < gamma)
    # ------------------------------------------------------------------
    # The Ants AI Challenge attack rule: an ant dies if any enemy is within
    # ``attackradius2`` Euclidean squared distance (5 by default — i.e.
    # Manhattan d=2 on cardinal axes, d=2 on diagonals up to (1,2)).
    #
    # alpha = "could attack right now"
    # beta  = "could attack next turn after one move (incl. me staying)"
    # gamma = "could attack within two moves"
    #
    # These match Strategy.java:1726, 1732, 1742 exactly.
    def is_alpha_dist(self, t1: Tile, t2: Tile) -> bool:
        dr = self.dist_row(t1, t2)
        dc = self.dist_col(t1, t2)
        return (dc <= 1 and dr <= 2) or (dc == 2 and dr <= 1)

    def is_beta_dist(self, t1: Tile, t2: Tile) -> bool:
        dr = self.dist_row(t1, t2)
        dc = self.dist_col(t1, t2)
        if dr + dc <= 4:
            if (dr == 0 and dc == 4) or (dc == 0 and dr == 4):
                return False
            return True
        return False

    def is_gamma_dist(self, t1: Tile, t2: Tile) -> bool:
        dr = self.dist_row(t1, t2)
        dc = self.dist_col(t1, t2)
        if dr + dc <= 5:
            if (dr == 0 and dc == 5) or (dc == 0 and dr == 5):
                return False
            return True
        return False

    # ------------------------------------------------------------------
    # Main turn entry point
    # ------------------------------------------------------------------
    def do_turn(self, ants: Ants) -> None:
        self.start_time_ms = time.monotonic() * 1000.0
        self.turn += 1
        self._ensure_initialized(ants)
        self._prune_water_neighbors(ants)
        self._sync_engine_state(ants)
        self._actions(ants)

    def _sync_engine_state(self, ants: Ants) -> None:
        """Mirror the Ants engine's view of the world onto our Tile graph.

        Called every turn. xathis's ``Connection`` (Connection.java) does
        equivalent work after each engine update.
        """
        # Reset per-turn flags on tiles. Persistent fields (explore_value,
        # neighbors, is_hill, etc.) are not touched here.
        for row in self.tiles:
            for tile in row:
                if tile.tile_type != WATER:  # keep water permanent
                    tile.tile_type = LAND
                tile.ant = None
                tile.old_ant = None

        # Refresh ant / food / hill positions.
        self.my_ants = []
        self.enemy_ants = []
        self.foods = []
        self.my_hills = []
        self.enemy_hills = []
        self.dangered_ants = []

        for (r, c), owner in ants.ant_list.items():
            tile = self.tiles[r][c]
            tile.tile_type = owner  # 0 = me, 1..9 = enemy player N
            ant = Ant(tile)
            tile.ant = ant
            tile.old_ant = ant
            if owner == MY_ANT:
                self.my_ants.append(ant)
            else:
                self.enemy_ants.append(ant)

        for (r, c) in ants.food_list:
            tile = self.tiles[r][c]
            if tile.tile_type == LAND:  # don't override an ant on the food
                tile.tile_type = FOOD
            self.foods.append(tile)

        for (r, c), owner in ants.hill_list.items():
            tile = self.tiles[r][c]
            tile.is_hill = True
            tile.hill_player = owner
            if owner == MY_ANT:
                self.my_hills.append(tile)
            else:
                self.enemy_hills.append(tile)

        # Stash the engine reference so do_move can call issue_order.
        self._engine = ants

    # ------------------------------------------------------------------
    # Phase ladder (Strategy.java:203)
    # ------------------------------------------------------------------
    def _actions(self, ants: Ants) -> None:
        # Phases marked TODO are stubs; they'll be filled in commit by
        # commit. The order matches Strategy.actions() exactly.
        self._init_turn()
        self._calc_num_close_enemies()
        self._init_missions()
        self._enemy_hills()
        self._food()
        self._init_explore()
        self._create_areas()
        self._fight()
        self._defence()
        self._approach_enemies()
        self._attack_detached_enemies()
        self._escape_enemies()
        self._distribute(only_near_enemy=True)
        self._explore()
        self._do_missions()
        self._create_missions()
        self._distribute(only_near_enemy=False)
        self._clean_areas()

    # ------------------------------------------------------------------
    # Phase stubs (filled in subsequent commits)
    # ------------------------------------------------------------------
    def _init_turn(self) -> None:
        """TODO: dangered/indirectly-dangered flags, willStay detection,
        gammaDistEnemies precomputation. Strategy.java:78-202."""
        pass

    def _calc_num_close_enemies(self) -> None:
        """TODO: BFS from each enemy ant to count close own ants.
        Strategy.java:224-254."""
        pass

    def _init_missions(self) -> None:
        """TODO: re-attach ongoing missions to current ants.
        Strategy.java:263-280."""
        pass

    def _enemy_hills(self) -> None:
        """TODO: send up to 4 attackers per enemy hill via BFS.
        Strategy.java:486-514."""
        pass

    def _food(self) -> None:
        """TODO: multi-source BFS from food tiles, first ant claims.
        Strategy.java:516-585."""
        pass

    def _init_explore(self) -> None:
        """TODO: reset exploreValue for tiles within 10 steps of an ant.
        Strategy.java:891-916."""
        pass

    def _create_areas(self) -> None:
        """TODO: territory flood-fill + border tile detection.
        Strategy.java:678-771."""
        pass

    def _fight(self) -> None:
        """TODO: gamma-group minimax with dep tables + alpha-beta cuts.
        Strategy.java:781-874."""
        pass

    def _defence(self) -> None:
        """TODO: hill defender interception via path BFS.
        Strategy.java:368-484."""
        pass

    def _approach_enemies(self) -> None:
        """TODO: A* path toward closest enemy for fight-area ants.
        Strategy.java:876-889."""
        pass

    def _attack_detached_enemies(self) -> None:
        """TODO: pile on isolated enemy ants.
        Strategy.java:587-593."""
        pass

    def _escape_enemies(self) -> None:
        """TODO: dangered ants pick the safest neighbor via 8-step BFS.
        Strategy.java:595-666."""
        pass

    def _distribute(self, only_near_enemy: bool) -> None:
        """TODO: spread out by maximizing reachable-tile count.
        Strategy.java:990-1014."""
        pass

    def _explore(self) -> None:
        """TODO: 11-step BFS, move toward highest exploreValue frontier.
        Strategy.java:917-988."""
        pass

    def _do_missions(self) -> None:
        """TODO: A* each mission ant toward its target tile.
        Strategy.java:281-304."""
        pass

    def _create_missions(self) -> None:
        """TODO: assign new missions to idle ants in fight areas.
        Strategy.java:313-336."""
        pass

    def _clean_areas(self) -> None:
        """TODO: reset is_in_my_area flags for next turn.
        Strategy.java:773-777."""
        pass

    # ------------------------------------------------------------------
    # Move issuing
    # ------------------------------------------------------------------
    def do_move(self, src: Tile, dest: Tile, info: str = "") -> bool:
        """Issue a move from ``src`` to ``dest`` (must be a direct neighbor).

        Mirrors ``Strategy.doMove`` (Strategy.java:1656). Returns True if
        the move was issued. Does not perform safety checks — those are
        the caller's responsibility (most phase methods gate via
        ``is_tile_safe``).
        """
        if src.ant is None:
            return False
        if dest is src:
            src.ant.has_moved = True
            return True
        direction = src.dir_to(dest)
        # Update the tile graph.
        dest.tile_type = src.tile_type
        dest.ant = src.ant
        src.tile_type = LAND
        src.ant.tile = dest
        src.ant.has_moved = True
        src.ant = None
        # Tell the engine.
        self._engine.issue_order((src.row, src.col, direction))
        return True


def main() -> None:
    try:
        Ants.run(XathisBot())
    except KeyboardInterrupt:
        print("ctrl-c, leaving ...")


if __name__ == "__main__":
    main()
