# main.py

from simulation.player import create_player, ShotType, Weakness, Strength, TournamentResult, InjurySeverity
from simulation.match_formats import create_match_format
from simulation.match import Surface, Weather
from simulation.engine import SimulationEngine
from models.ml_model import MLModel
from models.odds_calculator import OddsCalculator
import config

def main():
    # Create players
    player1 = create_player(
        name="Roger",
        country="Switzerland",
        stats={
            'serve_accuracy': 0.65,
            'groundstroke_accuracy': 0.75,
            'volley_accuracy': 0.70,
            'speed': 85,
            'stamina': 90,
            'mental_strength': 95
        },
        preferences={
            ShotType.FOREHAND: 0.4,
            ShotType.BACKHAND: 0.3,
            ShotType.SLICE_FOREHAND: 0.1,
            ShotType.SLICE_BACKHAND: 0.1,
            ShotType.VOLLEY_FOREHAND: 0.05,
            ShotType.VOLLEY_BACKHAND: 0.03,
            ShotType.SMASH: 0.02
        },
        atp_rank=3,
        previous_atp_rank=4,
        weaknesses=[Weakness.BACKHAND],
        strengths=[Strength.FOREHAND, Strength.SERVE],
        previous_tournament_results=[TournamentResult.SEMIFINALIST, TournamentResult.WINNER, TournamentResult.QUARTERFINALIST],
        current_injuries={"wrist": InjurySeverity.MINOR},
        previous_injuries={"knee": InjurySeverity.MODERATE},
        wins_vs_opponents={"Novak": 23}
    )

    player2 = create_player(
        name="Novak",
        country="Serbia",
        stats={
            'serve_accuracy': 0.62,
            'groundstroke_accuracy': 0.78,
            'volley_accuracy': 0.68,
            'speed': 90,
            'stamina': 95,
            'mental_strength': 98
        },
        preferences={
            ShotType.FOREHAND: 0.35,
            ShotType.BACKHAND: 0.35,
            ShotType.SLICE_FOREHAND: 0.08,
            ShotType.SLICE_BACKHAND: 0.12,
            ShotType.VOLLEY_FOREHAND: 0.04,
            ShotType.VOLLEY_BACKHAND: 0.04,
            ShotType.SMASH: 0.02
        },
        atp_rank=1,
        previous_atp_rank=1,
        weaknesses=[Weakness.VOLLEY], 
        strengths=[Strength.FOREHAND, Strength.SERVE],
        previous_tournament_results=[TournamentResult.WINNER, TournamentResult.FINALIST, TournamentResult.WINNER],
        current_injuries={},  # No current injuries
        previous_injuries={"elbow": InjurySeverity.SEVERE},
        wins_vs_opponents={"Roger": 27}
    )

    # Create match format
    match_format = create_match_format('grand_slam')
    
    # Specify surface
    surface = Surface.HARD  # or Surface.CLAY, Surface.GRASS, Surface.CARPET
    is_indoor = False  # or True for indoor matches
    weather = Weather.SUNNY  # or Weather.CLOUDY, Weather.WINDY, Weather.RAINY
    event_country = "USA"  # or any other country where the event is taking place
    
    # Initialize ML model and odds calculator
    ml_model = MLModel(config.ML_MODEL_CONFIG[config.DEFAULT_MODEL]['path'])
    odds_calculator = OddsCalculator()

    # Create simulation engine
    engine = SimulationEngine(
        player1, 
        player2, 
        match_format, 
        surface, 
        is_indoor, 
        weather, 
        event_country,
        ml_model, 
        odds_calculator
    )

    # Run simulation
    engine.run_simulation()

    # Get and print final results
    results = engine.get_match_results()
    print("\nFinal Match Results:")
    print(f"Winner: {results['winner']}")
    print(f"Final Score: {results['score']}")
    print("Match Statistics:")
    for player, stats in results['stats'].items():
        print(f"  {player}:")
        for stat, value in stats.items():
            print(f"    {stat}: {value}")
    print(f"Final Odds: {results['final_odds']}")

if __name__ == "__main__":
    main()