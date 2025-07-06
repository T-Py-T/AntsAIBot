# Ants AI Challenge Python Bot

This project is a modernized, Pythonic implementation for the [Ants AI Challenge](http://ants.aichallenge.org/ants_tutorial.php). It provides a clean, maintainable codebase for developing, testing, and visualizing AI bots that compete in the Ants game simulation.

## Purpose

- **Develop and test AI bots** for the Ants game, following best Python practices.
- **Compete your custom bot** (`src/bots/bot.py`) against other agents in a reproducible, scriptable environment.
- **Visualize and analyze** game replays to improve your bot's strategy.

## Project Structure

``` sh
AntsAIBot/
├── src/
│   ├── ants/        # Game engine and logic
│   ├── bots/        # Your bot and (optionally) other agents
│   └── tools/       # Game runner and utilities
├── visualizer/      # Visualization tools for replays
├── scripts/         # Shell scripts for running games
├── maps/            # Game maps
├── game_logs/       # Game logs and replays
```

## Your Bot

- The main bot you will develop and test is: `src/bots/bot.py`
- This bot will compete against itself or other agents in the game engine.

## How to Test Your Bot Against Example Bots

1. **Install dependencies** (using [uv](https://github.com/astral-sh/uv) or pip):

   ```sh
   uv pip install -r pyproject.toml
   # or
   pip install colorama pytest
   ```

2. **Run a game with your bot against itself:**

   ```sh
   PYTHONPATH=. python3 src/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 1000 --map_file maps/maze/maze_04p_01.map "python3 src/bots/bot.py" "python3 src/bots/bot.py" "python3 src/bots/bot.py" "python3 src/bots/bot.py"
   ```
   
   - This will run a 4-player game with your bot in all slots.
   - Game logs and a replay file will be saved in `game_logs/`.

3. **Visualize the results:**

   ```sh
   python3 visualizer/visualize_locally.py game_logs/0.replay
   ```

   - This will generate and open an HTML visualization of the game replay.

4. **(Optional) Add more bots:**
   - Place additional bot scripts in `src/bots/` and update the command above to include them.

## Future Expectations

- **Internal Testing:**

  - We plan to add automated tests to validate the functions and logic in the engine and bots.
  - This will help catch errors early and confirm that code changes produce the expected results.
  - Tests will be written using `pytest` and can be run with:

    ```sh
    pytest
    ```

---

For more details on the Ants AI Challenge, see the [official tutorial](http://ants.aichallenge.org/ants_tutorial.php).
