# Quick Reference: Strategy Pattern Implementation

## 🚀 Quick Start

### Run Recommendations
```bash
python3 -m src.main                    # Default (Balanced)
python3 -m src.main genre-first        # Genre priority
python3 -m src.main popularity-first   # Trending songs
python3 -m src.main vibe-mode          # Mood & energy
python3 -m src.main compare            # Compare all strategies
```

### Code Usage
```python
from src.recommender import Recommender, UserProfile
from src.scoring_strategies import get_strategy

# Default = BalancedStrategy
recommender = Recommender(songs)

# Change strategy
strategy = get_strategy("genre-first")
recommender.set_strategy(strategy)

# Or specify on creation
recommender = Recommender(songs, strategy=strategy)
```

## 📊 Strategy Comparison

| Strategy | Primary Focus | Best For |
|----------|---------------|----------|
| **Balanced** | All factors equally | Default, well-rounded |
| **Genre-First** | Genre match (+5.0) | Strict genre lovers |
| **Popularity-First** | Trending, artist fame | Discovering hits |
| **Vibe-Mode** | Mood & energy (+3.0) | Playlist creation |

## 🔧 Add New Strategy

```python
# In src/scoring_strategies.py

class MyStrategy(ScoringStrategy):
    def score_song(self, user: UserProfile, song: Song) -> float:
        score = 0.0
        # Your logic here
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        return f"My strategy scored {song.title}: {self.score_song(user, song):.2f}"

# Register it
AVAILABLE_STRATEGIES = {
    "balanced": BalancedStrategy,
    "genre-first": GenreFirstStrategy,
    "popularity-first": PopularityFirstStrategy,
    "vibe-mode": VibeModeStrategy,
    "my-strategy": MyStrategy,  # ← Add here
}
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/scoring_strategies.py` | All strategy implementations |
| `src/recommender.py` | Recommender class with strategy support |
| `src/main.py` | CLI with strategy selection |
| `tests/test_recommender.py` | Unit tests |
| `STRATEGY_PATTERN_GUIDE.md` | Full documentation |

## ✨ Key Methods

```python
# Recommender class
recommender = Recommender(songs)
recommender.set_strategy(strategy)           # Change strategy
recommender.get_strategy_name()              # Get current strategy name
recommender.recommend(user, k=5)             # Get recommendations
recommender.score_song(user, song)           # Score a single song
recommender.explain_recommendation(user, song) # Explain score

# Strategies
strategy = get_strategy("genre-first")       # Get by name
score = strategy.score_song(user, song)      # Score song
explanation = strategy.explain_score(user, song) # Explain it
```

## 🎯 Scoring Weights by Strategy

### Balanced
- Genre: +1.0, Mood: +2.0, Energy: +1.0, Popularity: +0.5

### Genre-First
- Genre: +5.0 (dominant), Mood: +1.0, Rest: minimal

### Popularity-First  
- Popularity: +1.0, Streams: +1.0, Artist: +0.6, Mood/Genre: +0.5

### Vibe-Mode
- Mood: +3.0, Energy: +2.0, Genre: +0.5, Acoustic: +0.5

## 📝 Testing

```bash
pytest tests/test_recommender.py -v          # Run all tests
pytest tests/test_recommender.py::test_name  # Run specific test
```

## 🔍 Debug/Inspect

```python
# See what strategy is active
print(recommender.get_strategy_name())  # "BalancedStrategy"

# List all available strategies
from src.scoring_strategies import AVAILABLE_STRATEGIES
print(list(AVAILABLE_STRATEGIES.keys()))

# Get full score breakdown
user = UserProfile(...)
song = song_list[0]
score = recommender.score_song(user, song)
explanation = recommender.explain_recommendation(user, song)
print(f"Score: {score}\n{explanation}")
```

## 📚 Design Pattern: Strategy

**Purpose:** Encapsulate ranking algorithms to allow runtime switching

**Components:**
- `ScoringStrategy` - Abstract interface
- Concrete strategies - `BalancedStrategy`, `GenreFirstStrategy`, etc.
- `Recommender` - Uses strategy to score songs
- `AVAILABLE_STRATEGIES` - Registry for lookup

**Benefit:** New strategies don't require changing existing code

## 🎬 Example: Full Workflow

```python
from src.recommender import Recommender, Song, UserProfile
from src.scoring_strategies import get_strategy

# 1. Load songs
songs = [
    Song(id=1, title="Song A", artist="Artist A", genre="rock", 
         mood="intense", energy=0.8, ..., year_released=2023, 
         popularity_score=75, explicit_content=0, artist_followers=2000,
         spotify_streams=200, radio_friendly=0.8),
    # More songs...
]

# 2. Create user profile
user = UserProfile(
    favorite_genre="rock",
    favorite_mood="intense",
    target_energy=0.8,
    likes_acoustic=False
)

# 3. Create recommender with strategy
strategy = get_strategy("vibe-mode")
recommender = Recommender(songs, strategy=strategy)

# 4. Get recommendations
recommendations = recommender.recommend(user, k=5)

# 5. Show results with explanations
for rank, song in enumerate(recommendations, 1):
    score = recommender.score_song(user, song)
    explanation = recommender.explain_recommendation(user, song)
    print(f"#{rank}. {song.title}")
    print(f"Score: {score:.2f}")
    print(explanation)
```

## 🚨 Common Issues

**Problem:** Strategy not changing  
**Solution:** Call `recommender.set_strategy(new_strategy)` - it doesn't auto-reload

**Problem:** Custom strategy not found  
**Solution:** Make sure it's added to `AVAILABLE_STRATEGIES` dict in scoring_strategies.py

**Problem:** Tests failing after changes  
**Solution:** All Song objects need: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness, year_released, popularity_score, explicit_content, artist_followers, spotify_streams, radio_friendly

## 💡 Pro Tips

1. **Compare strategies:** Run `python3 -m src.main compare` to see differences
2. **User preferences:** Store user's favorite strategy and apply on load
3. **Hybrid approach:** Combine scores from multiple strategies
4. **A/B testing:** Show different strategies to different users
5. **Performance:** Profile strategies to find speed/quality tradeoffs
