from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .scoring_strategies import ScoringStrategy

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    year_released: int
    popularity_score: float
    explicit_content: int
    artist_followers: float
    spotify_streams: float
    radio_friendly: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    prefers_modern: bool = True  # True for modern era (2015+), False for classic era (<2015)
    explicit_tolerance: bool = True  # False if user wants no explicit content
    minimum_popularity: int = 30  # Minimum popularity score threshold
    values_artist_credibility: bool = True  # Whether to consider artist followers

class Recommender:
    """
    OOP implementation of the recommendation logic with Strategy pattern support.
    Required by tests/test_recommender.py
    
    Supports multiple scoring strategies that can be swapped at runtime.
    Includes optional diversity and fairness logic to prevent too many songs from 
    the same artist or genre in the top results.
    """
    def __init__(self, songs: List[Song], strategy: Optional["ScoringStrategy"] = None, 
                 enable_diversity: bool = True):
        """
        Initialize recommender with optional scoring strategy.
        
        Args:
            songs: List of Song objects to recommend from
            strategy: ScoringStrategy instance. If None, uses BalancedStrategy by default.
            enable_diversity: If True, applies diversity penalties to prevent too many songs
                            from the same artist or genre in recommendations.
        """
        self.songs = songs
        self.strategy = strategy
        self.enable_diversity = enable_diversity
        
        # Lazy import to avoid circular dependencies
        if self.strategy is None:
            from .scoring_strategies import BalancedStrategy
            self.strategy = BalancedStrategy()
    
    def set_strategy(self, strategy: "ScoringStrategy") -> None:
        """Change the scoring strategy at runtime."""
        self.strategy = strategy
    
    def get_strategy_name(self) -> str:
        """Get the name of the current strategy."""
        return self.strategy.__class__.__name__

    def _get_diversity_penalty(self, song: Song, selected_songs: List[Song]) -> float:
        """
        Calculate diversity penalty to encourage variety in recommendations.
        
        Penalizes songs based on how many songs from the same artist and genre
        are already in the selected recommendations.
        
        Artist penalty structure:
        - 1st song from artist: 0.0 (no penalty)
        - 2nd song from artist: -0.5
        - 3rd song from artist: -1.5
        - 4th+ songs from artist: -3.0
        
        Genre penalty structure:
        - 1st song from genre: 0.0 (no penalty)
        - 2nd song from genre: -0.3
        - 3rd+ songs from genre: -0.8
        
        Args:
            song: The song to calculate penalty for
            selected_songs: List of songs already selected in recommendations
            
        Returns:
            Total penalty as a negative float (0.0 if no penalty)
        """
        penalty = 0.0
        
        # Count songs by this artist already selected
        artist_count = sum(1 for s in selected_songs if s.artist.lower() == song.artist.lower())
        if artist_count >= 1:
            if artist_count == 1:
                penalty -= 0.5
            elif artist_count == 2:
                penalty -= 1.5
            else:  # 3 or more
                penalty -= 3.0
        
        # Count songs in this genre already selected
        genre_count = sum(1 for s in selected_songs if s.genre.lower() == song.genre.lower())
        if genre_count >= 1:
            if genre_count == 1:
                penalty -= 0.3
            else:  # 2 or more
                penalty -= 0.8
        
        return penalty

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Recommend songs using the current scoring strategy.
        
        If diversity is enabled, builds recommendations iteratively with diversity penalties
        to prevent too many songs from the same artist or genre.
        Otherwise, simply returns top-k by score.
        
        Args:
            user: UserProfile with user preferences
            k: Number of recommendations to return
            
        Returns:
            List of k recommended Song objects
        """
        if not self.enable_diversity:
            # Original behavior: score all songs and return top k by score
            scored_songs = [(song, self.score_song(user, song)) for song in self.songs]
            return [song for song, _ in sorted(scored_songs, key=lambda x: (-x[1], x[0].title))[:k]]
        
        # Diversity-aware recommendation: build list iteratively with penalties
        selected_songs: List[Song] = []
        remaining_songs = list(self.songs)
        
        for _ in range(k):
            if not remaining_songs:
                break
            
            # Score all remaining songs with diversity penalties applied
            best_song = None
            best_score = -float('inf')
            best_index = -1
            
            for idx, song in enumerate(remaining_songs):
                base_score = self.score_song(user, song)
                diversity_penalty = self._get_diversity_penalty(song, selected_songs)
                adjusted_score = base_score + diversity_penalty
                
                # Sort by adjusted score (highest first), then by title for consistency
                if adjusted_score > best_score or (adjusted_score == best_score and 
                                                   (best_song is None or song.title < best_song.title)):
                    best_song = song
                    best_score = adjusted_score
                    best_index = idx
            
            if best_song is not None and best_index >= 0:
                selected_songs.append(best_song)
                remaining_songs.pop(best_index)
        
        return selected_songs
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score a song using the current strategy."""
        return self.strategy.score_song(user, song)

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song is recommended using the current strategy."""
        return self.strategy.explain_score(user, song)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and convert numeric columns to appropriate types."""
    import csv
    
    songs = []
    # Define which columns should be converted to float
    float_columns = {'energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness', 
                    'popularity_score', 'artist_followers', 'spotify_streams', 'radio_friendly'}
    # Define which columns should be converted to int
    int_columns = {'id', 'year_released', 'explicit_content'}
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numeric values to appropriate types
            for col in float_columns:
                row[col] = float(row[col])
            for col in int_columns:
                row[col] = int(row[col])
            songs.append(row)
    
    print(f"Loading songs from {csv_path}...")
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Recommend songs using functional approach with advanced multi-factor scoring.
    
    Comprehensive scoring breakdown:
    +1.0 point for genre match
    +2.0 points for mood match
    +0.0 to 1.0 points for energy similarity (Euclidean distance)
    +0.0 to 0.5 points for popularity boost (normalized 0-100)
    +0.0 to 1.0 points for era preference bonus
    +0.0 to 0.3 points for radio-friendly bonus
    +0.0 to 0.3 points for artist credibility (followers)
    +0.0 to 0.4 points for streaming popularity
    -1.0 penalty for explicit content if user prefers clean music
    -0.3 penalty if below minimum popularity threshold
    
    Args:
        user_prefs: Dict with keys 'favorite_genre', 'favorite_mood', 'target_energy',
                    'prefers_modern' (bool), 'explicit_tolerance' (bool),
                    'minimum_popularity' (int), 'values_artist_credibility' (bool)
        songs: List of song dictionaries with new attributes
        k: Number of recommendations to return
    
    Returns:
        List of tuples: (song_dict, score, explanation)
    """
    # Set default preferences if not provided
    prefers_modern = user_prefs.get('prefers_modern', True)
    explicit_tolerance = user_prefs.get('explicit_tolerance', True)
    minimum_popularity = user_prefs.get('minimum_popularity', 30)
    values_artist_credibility = user_prefs.get('values_artist_credibility', True)
    
    scored_songs = []
    
    for song in songs:
        score = 0.0
        explanation_parts = []
        
        # +1.0 point for genre match
        if song['genre'].lower() == user_prefs['favorite_genre'].lower():
            score += 1.0
            explanation_parts.append(f"✓ +1.0 Genre match ({song['genre']})")
        else:
            explanation_parts.append(f"✗ Genre mismatch (song: {song['genre']}, preference: {user_prefs['favorite_genre']})")
        
        # +2.0 points for mood match
        if song['mood'].lower() == user_prefs['favorite_mood'].lower():
            score += 2.0
            explanation_parts.append(f"✓ +2.0 Mood match ({song['mood']})")
        else:
            explanation_parts.append(f"✗ Mood mismatch (song: {song['mood']}, preference: {user_prefs['favorite_mood']})")
        
        # Energy similarity: Euclidean distance (0.0 to 1.0 points)
        energy_similarity = 1.0 - abs(user_prefs['target_energy'] - song['energy'])
        energy_diff = abs(user_prefs['target_energy'] - song['energy'])
        score += energy_similarity
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy similarity (user: {user_prefs['target_energy']:.2f}, song: {song['energy']:.2f}, diff: {energy_diff:.2f})")
        
        # === ERA-BASED SCORING ===
        current_year = 2024
        if prefers_modern:
            # Modern preference: curve favors newer songs
            if song['year_released'] >= 2015:
                era_bonus = min(1.0, 0.8 * (1 - (song['year_released'] - 2015) / 50))
            else:
                era_bonus = max(0.0, 0.3 - (2015 - song['year_released']) / 100)
            era_pref_text = "modern era (≥2015)"
        else:
            # Classic preference: rewards older songs
            if song['year_released'] < 2015:
                era_bonus = min(1.0, 0.8 * (1 - (current_year - song['year_released']) / 100))
            else:
                era_bonus = max(0.0, 0.3 - (song['year_released'] - 2015) / 100)
            era_pref_text = "classic era (<2015)"
        
        score += era_bonus
        explanation_parts.append(f"✓ +{era_bonus:.2f} Era preference ({song['year_released']}, user prefers {era_pref_text})")
        
        # === POPULARITY & CREDIBILITY SCORING ===
        # +0.0 to 0.5 points for popularity boost
        popularity_boost = (song['popularity_score'] / 100.0) * 0.5
        score += popularity_boost
        explanation_parts.append(f"✓ +{popularity_boost:.2f} Popularity boost (score: {song['popularity_score']}/100)")
        
        # Penalty if below minimum popularity threshold
        if song['popularity_score'] < minimum_popularity:
            score -= 0.3
            explanation_parts.append(f"✗ -0.3 Below minimum popularity ({song['popularity_score']} < {minimum_popularity})")
        
        # +0.0 to 0.3 points for artist credibility
        if values_artist_credibility:
            normalized_followers = min(1.0, song['artist_followers'] / 5000.0)
            artist_credibility = normalized_followers * 0.3
            score += artist_credibility
            explanation_parts.append(f"✓ +{artist_credibility:.2f} Artist credibility ({song['artist_followers']}k followers)")
        
        # +0.0 to 0.4 points for streaming popularity
        stream_score = min(0.4, (song['spotify_streams'] / 700.0) * 0.4)
        score += stream_score
        explanation_parts.append(f"✓ +{stream_score:.2f} Streaming popularity ({song['spotify_streams']}M streams)")
        
        # === RADIO COMPATIBILITY & EXPLICIT CONTENT ===
        # +0.0 to 0.3 bonus for radio-friendly
        radio_bonus = song['radio_friendly'] * 0.3
        score += radio_bonus
        explanation_parts.append(f"✓ +{radio_bonus:.2f} Radio-friendly factor ({song['radio_friendly']:.2f})")
        
        # -1.0 penalty for explicit content if user prefers clean music
        if song['explicit_content'] == 1:
            if explicit_tolerance:
                explanation_parts.append(f"ℹ Explicit content (user accepts)")
            else:
                score -= 1.0
                explanation_parts.append(f"✗ -1.0 Explicit content penalty (user prefers clean music)")
        
        score = max(0.0, score)  # Ensure non-negative score
        explanation = f"Total: {score:.2f} points\n" + "\n".join(explanation_parts)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending, then by title for tie-breaking
    scored_songs.sort(key=lambda x: (-x[1], x[0]['title']))
    
    # Return top k songs
    return scored_songs[:k]
