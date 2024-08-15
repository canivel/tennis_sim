# main.py

from simulation.player import create_player, ShotType
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
        wins_vs_opponents={"Novak": 23}
    )

    player2 = create_player(
        name="Novak",
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
        wins_vs_opponents={"Roger": 27}
    )

    # Create match format
    match_format = create_match_format('grand_slam')
    
    # Specify surface
    surface = Surface.HARD  # or Surface.CLAY, Surface.GRASS, Surface.CARPET
    is_indoor = False  # or True for indoor matches
    weather = Weather.SUNNY  # or Weather.CLOUDY, Weather.WINDY, Weather.RAINY
    event_country = "USA"  # or any other country where the event is taking plac
    
    # Initialize ML model and odds calculator
    ml_model = MLModel(config.ML_MODEL_CONFIG[config.DEFAULT_MODEL]['path'])
    odds_calculator = OddsCalculator()

    # Create and run simulation
    engine = SimulationEngine(
        player1, 
        player2, 
        match_format, 
        surface, 
        is_indoor, 
        weather, 
        event_country,  # Add this line
        ml_model, 
        odds_calculator
    )
    # Run simulation with periodic updates
    while not engine.match.is_match_over():
        event = engine.generate_next_event()
        engine.process_event(event)
        
        # Print updates every 10 events
        if len(engine.recent_events) % 10 == 0:
            print(f"Current score: {engine.match.get_score()}")
            print(f"Current odds: {engine.current_odds}")
            print("---")

    # Print final results
    results = engine.get_match_results()
    print(f"Match winner: {results['winner']}")
    print(f"Final score: {results['score']}")
    print(f"Match statistics: {results['stats']}")
    print(f"Final odds: {results['final_odds']}")

if __name__ == "__main__":
    main()