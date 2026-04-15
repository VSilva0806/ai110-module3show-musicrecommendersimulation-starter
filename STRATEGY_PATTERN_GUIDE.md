# Music Recommender - Strategy Pattern Guide

## Overview

The music recommender system has been refactored to use the **Strategy Pattern**, allowing you to easily switch between different scoring modes without modifying the core recommendation logic.

## Available Strategies

### 1. **Balanced Strategy** (Default)
- **Name:** `balanced`
- **Description:** Considers all factors equally
- **Scoring Weights:**
  - Genre match: +1.0
  - Mood match: +2.0
  - Energy similarity: +0.0 to 1.0
  - Popularity boost: +0.0 to 0.5
  - Era preference: +0.0 to 1.0
  - Artist credibility: +0.0 to 0.3
  - Streaming popularity: +0.0 to 0.4
  - Radio-friendly bonus: +0.0 to 0.3
- **Best For:** General recommendations with well-rounded consideration

### 2. **Genre-First Strategy**
- **Name:** `genre-first`
- **Description:** Heavily prioritizes genre matching above all else
- **Scoring Weights:**
  - Genre match: +5.0 (primary focus)
  - Mood match: +1.0
  - Energy similarity: +0.0 to 0.3 (minimal)
  - Popularity: +0.0 to 0.3 (minimal)
- **Best For:** Users who have strong genre preferences and want exact matches

### 3. **Popularity-First Strategy**
- **Name:** `popularity-first`
- **Description:** Prioritizes streaming popularity and artist credibility
- **Scoring Weights:**
  - Popularity score: +0.0 to 1.0 (high weight)
  - Streaming popularity: +0.0 to 1.0 (high weight)
  - Artist credibility: +0.0 to 0.6 (high weight)
  - Genre match: +0.5
  - Mood match: +0.5
- **Best For:** Discovering trending and well-established songs

### 4. **Vibe-Mode Strategy**
- **Name:** `vibe-mode`
- **Description:** Prioritizes mood and energy matching for the perfect listening experience
- **Scoring Weights:**
  - Mood match: +3.0 (primary focus)
  - Energy similarity: +0.0 to 2.0 (high weight)
  - Genre match: +0.5
  - Acoustic preference: +0.3 to 0.5
  - Popularity: +0.0 to 0.2 (minimal)
- **Best For:** Creating playlists with specific emotional energy

## How to Use

### From Command Line

#### Run with default (Balanced) strategy:
```bash
python3 -m src.main
```

#### Run with specific strategy:
```bash
python3 -m src.main genre-first
python3 -m src.main popularity-first
python3 -m src.main vibe-mode
```

#### Compare all strategies:
```bash
python3 -m src.main compare
```

### In Python Code

#### Using OOP approach with strategies:

```python
from src.recommender import Song, UserProfile, Recommender
from src.scoring_strategies import get_strategy

# Load songs
songs = [...]  # Your Song objects

# Create user profile
user = UserProfile(
    favorite_genre="pop",
    favorite_mood="happy",
    target_energy=0.8,
    likes_acoustic=False
)

# Create recommender with balanced strategy (default)
recommender = Recommender(songs)
recommendations = recommender.recommend(user, k=5)

# Switch to a different strategy at runtime
genre_first_strategy = get_strategy("genre-first")
recommender.set_strategy(genre_first_strategy)
recommendations = recommender.recommend(user, k=5)

# Or create recommender with specific strategy
popularity_strategy = get_strategy("popularity-first")
recommender = Recommender(songs, strategy=popularity_strategy)
recommendations = recommender.recommend(user, k=5)
```

#### Get explanations for recommendations:

```python
for song in recommendations:
    score = recommender.score_song(user, song)
    explanation = recommender.explain_recommendation(user, song)
    print(f"Song: {song.title}")
    print(f"Score: {score:.2f}")
    print(f"Explanation:\n{explanation}")
```

### Creating Custom Strategies

To add a new ranking technique, create a class that inherits from `ScoringStrategy`:

```python
from src.scoring_strategies import ScoringStrategy
from src.recommender import Song, UserProfile

class MyCustomStrategy(ScoringStrategy):
    """Custom strategy based on your ranking logic."""
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Implement your scoring logic here."""
        score = 0.0
        
        # Your custom logic
        if song.genre.lower() == user.favorite_genre.lower():
            score += 10.0  # Heavy weight your factors
        
        # More custom logic...
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Provide explanation for how the score was calculated."""
        return f"Custom strategy scored {song.title}: {self.score_song(user, song):.2f}"
```

Then register it in `AVAILABLE_STRATEGIES` in `scoring_strategies.py`:

```python
AVAILABLE_STRATEGIES = {
    "balanced": BalancedStrategy,
    "genre-first": GenreFirstStrategy,
    "popularity-first": PopularityFirstStrategy,
    "vibe-mode": VibeModeStrategy,
    "my-custom": MyCustomStrategy,  # Add your strategy
}
```

## Architecture

### Design Pattern: Strategy

The implementation uses the **Strategy Pattern** to encapsulate different ranking algorithms:

```
┌─────────────────────┐
│   Recommender       │
├─────────────────────┤
│ - songs: List[Song] │
│ - strategy: Strategy│  ◄─────┐
│ + score_song()      │        │
│ + recommend()       │        │
└─────────────────────┘        │
                               │
        ┌──────────────────────┴──────────────────────────────┐
        │                                                     │
    ┌───────────────────────┐                    ┌────────────────────┐
    │ ScoringStrategy (ABC) │                    │ ConcreteStrategies │
    ├───────────────────────┤                    ├────────────────────┤
    │ + score_song()        │                    │ BalancedStrategy   │
    │ + explain_score()     │◄───────────────────│ GenreFirstStrategy │
    └───────────────────────┘                    │ PopularityFirst... │
                                                  │ VibeModeStrategy   │
                                                  └────────────────────┘
```

### Benefits

1. **Modularity:** Each strategy is encapsulated in its own class
2. **Flexibility:** Switch strategies at runtime without restarting
3. **Extensibility:** Add new strategies without modifying existing code
4. **Testability:** Each strategy can be tested independently
5. **Maintainability:** Changes to one strategy don't affect others

## Example: Comparing Strategies

```python
from src.recommender import Song, UserProfile, Recommender
from src.scoring_strategies import AVAILABLE_STRATEGIES

# Define a test user
user = UserProfile(
    favorite_genre="rock",
    favorite_mood="intense",
    target_energy=0.7,
    likes_acoustic=False
)

# Load songs
songs = [...]  # Your songs

# Test each strategy
for strategy_name, strategy_class in AVAILABLE_STRATEGIES.items():
    strategy = strategy_class()
    recommender = Recommender(songs, strategy=strategy)
    recommendations = recommender.recommend(user, k=3)
    
    print(f"\n{strategy_name.upper()}")
    print("-" * 50)
    for i, song in enumerate(recommendations, 1):
        score = recommender.score_song(user, song)
        print(f"{i}. {song.title} (Score: {score:.2f})")
```

## File Structure

```
src/
├── recommender.py              # Core classes: Song, UserProfile, Recommender
├── scoring_strategies.py       # Strategy pattern implementation
├── main.py                     # CLI entry point with strategy selection
└── __init__.py

tests/
└── test_recommender.py         # Unit tests (backward compatible)
```

## Testing

All existing tests pass with the new strategy pattern:

```bash
pytest tests/test_recommender.py -v
```

The `Recommender` class maintains backward compatibility - when initialized without a strategy, it defaults to `BalancedStrategy`.

## Next Steps

1. **Experiment with strategies:** Try different strategies with various user profiles to see how rankings change
2. **Create custom strategies:** Design strategies tailored to specific use cases
3. **Performance optimization:** Profile different strategies to understand computational trade-offs
4. **User preferences:** Store strategy preferences per user for personalized recommendations
