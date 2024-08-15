# Tennis Match Simulation

This project simulates tennis matches using machine learning to predict outcomes and update odds in real-time. It features detailed player statistics, various match formats, and dynamic odds calculation.

## Features

- Realistic tennis match simulation
- Detailed player modeling including strengths, weaknesses, and injuries
- Support for different match formats (e.g., Grand Slam, ATP 1000)
- Real-time odds calculation and updating
- Machine learning model for predicting point outcomes
- Periodic model retraining during the match
- Comprehensive match statistics and final results

## Project Structure

```
tennis_simulation/
├── main.py
├── config.py
├── simulation/
│   ├── engine.py
│   ├── events.py
│   ├── player.py
│   ├── match.py
│   └── match_formats.py
├── models/
│   ├── ml_model.py
│   └── odds_calculator.py
└── train/
    ├── train_baseline_model.py
    └── data_generation.py
```

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/tennis-simulation.git
   cd tennis-simulation
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Train the initial ML model:
   ```
   python train/train_baseline_model.py
   ```

## Running a Simulation

To run a tennis match simulation:

```
python main.py
```

This will simulate a match between two pre-defined players and output periodic updates and final results.

# Features Used by the ML Model

1. **surface**: The playing surface (e.g., clay, grass, hard court). Different surfaces affect player performance.

2. **is_indoor**: Boolean indicating if the match is indoor or outdoor. Indoor conditions can affect play style and ball movement.

3. **weather**: Current weather conditions. Affects player comfort and ball behavior.

4. **event_country**: The country where the event is taking place. May impact player performance due to travel, time zones, etc.

5. **server**: The player currently serving (0 or 1). Serving can provide an advantage.

6. **receiver**: The player currently receiving (0 or 1). Complementary to server.

7. **set_score_1, set_score_2**: Current set scores for each player. Indicates match progress and potential momentum.

8. **game_score_1, game_score_2**: Current game scores within the set. Reflects immediate progress.

9. **point_score_1, point_score_2**: Current point scores within the game. Crucial for predicting immediate outcomes.

10. **current_set**: The current set number. Players may fatigue or change strategies as the match progresses.

11. **is_tiebreak, is_match_tiebreak**: Indicates special scoring situations that may affect player performance.

12. **fatigue_1, fatigue_2**: Fatigue levels for each player. Impacts performance as the match progresses.

13. **player1_serve_accuracy, player2_serve_accuracy**: Serve accuracy for each player. Critical for predicting service games.

14. **player1_ground_accuracy, player2_ground_accuracy**: Groundstroke accuracy. Important for rallies and return games.

15. **player1_volley_accuracy, player2_volley_accuracy**: Volley accuracy. Relevant for net play and certain strategies.

16. **player1_atp_rank, player2_atp_rank**: Current ATP rankings. Indicates overall player skill and recent performance.

17. **player1_previous_atp_rank, player2_previous_atp_rank**: Previous ATP rankings. Shows trend in player performance.

18. **player1_weakness, player2_weakness**: Known weaknesses of each player. Opponents may target these.

19. **player1_strength, player2_strength**: Known strengths of each player. Players often rely on these in crucial moments.

20. **player1_previous_tournament_results, player2_previous_tournament_results**: Recent tournament performances. Indicates current form.

21. **player1_country, player2_country**: Player nationalities. May affect performance in certain countries or conditions.

22. **player1_current_injuries, player2_current_injuries**: Any current injuries. Significantly impacts player performance.

23. **player1_previous_injuries, player2_previous_injuries**: Past injuries. May indicate potential vulnerabilities.

24. **current_shot_type**: The type of shot just played. Influences the likely next shot and its success probability.

25. **current_ball_speed**: Speed of the current shot. Affects the receiver's ability to return effectively.

26. **current_ball_spin**: Spin on the current shot. Impacts ball behavior and return difficulty.

27. **average_winning_odd, average_losing_odd**: Current match odds. Reflects overall match situation and momentum.

28. **player1_wins_vs_opponent, player2_wins_vs_opponent**: Head-to-head record. Indicates historical matchup dynamics.

29. **player1_aces, player2_aces**: Number of aces in the current match. Shows serving effectiveness.

30. **player1_double_faults, player2_double_faults**: Number of double faults. Indicates serving consistency or pressure.

31. **player1_winners, player2_winners**: Number of winners hit. Reflects aggressive and successful play.

32. **player1_unforced_errors, player2_unforced_errors**: Number of unforced errors. Indicates consistency and current form.

These features provide a comprehensive view of the current match state, player capabilities, historical performance, and immediate game situation, allowing the model to make informed predictions about point outcomes.

## ML Model Training and Updating

The machine learning model in this project is designed to improve its predictions as the match progresses. Here's how it works:

1. **Initial Training**: Before the simulation starts, an initial model is trained using synthetic data generated in `train/data_generation.py`. This provides a baseline for predictions.

2. **In-Match Updates**: The model is updated every odd-numbered game during the match. This allows the model to adapt to the specific dynamics of the ongoing match.

3. **Retraining Process**:

   - After each odd-numbered game, the `SimulationEngine` calls the `MLModel.update()` method.
   - This method uses the events from the last two games to retrain the model.
   - The model incorporates this new data to adjust its predictions for future points.

4. **Feature Updates**: The model considers various features including player statistics, current match state, and recent point outcomes to make its predictions.

5. **Odds Calculation**: After each point, the updated model is used to recalculate the match odds, providing real-time updates on the likelihood of each player winning.

## Customization

You can customize the simulation by modifying the following:

- Player attributes in `main.py`
- Match format in `config.py`
- ML model parameters in `models/ml_model.py`
- Odds calculation logic in `models/odds_calculator.py`

## Contributing

Contributions to improve the simulation accuracy, add new features, or optimize performance are welcome. Please submit a pull request with your proposed changes.

## License

[MIT License](LICENSE)
