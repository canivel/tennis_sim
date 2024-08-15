This `Match` class encapsulates the core logic of a tennis match, including:

1. Keeping track of the match state (scores, serving player, etc.)
2. Updating scores when a point is played
3. Determining when games, sets, and the match are over
4. Handling tiebreaks and match tiebreaks according to the specified match format

The `play_point` method is the main entry point for simulating the match. It takes a `PointOutcome` and optionally a winner, updates the match state accordingly, and handles transitions between games and sets.

The `get_match_state` method allows external components (like our simulation engine) to access the current state of the match without directly modifying it.

This structure allows for flexibility in how points are determined (which will be handled by our simulation engine) while maintaining the rules and flow of a tennis match.

Next, we should create the `simulation/engine.py` file, which will use this `Match` class along with our ML model and odds calculator to run the actual simulation. Shall we proceed with that?
