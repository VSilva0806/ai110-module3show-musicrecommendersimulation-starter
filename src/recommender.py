from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Recommend songs based on point-weighting strategy: +2.0 for genre match, +1.0 for mood match."""
        # Score every song in the catalog and sort by score (highest first), then by title
        scored_songs = [(song, self.score_song(user, song)) for song in self.songs]
        return [song for song, _ in sorted(scored_songs, key=lambda x: (-x[1], x[0].title))[:k]]
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score a song based on user profile using genre, mood, and energy matching.
        
        Scoring breakdown:
        +2.0 points for genre match
        +1.0 point for mood match
        +0.0 to 1.0 points for energy similarity (Euclidean distance)
        """
        score = 0.0
        
        # +2.0 points for genre match
        if song.genre.lower() == user.favorite_genre.lower():
            score += 2.0
        
        # +1.0 point for mood match
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
        
        # Energy similarity: Euclidean distance (0.0 to 1.0 points)
        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        score += energy_similarity
        
        return score

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song is recommended by breaking down the matching score."""
        score = self.score_song(user, song)
        explanation_parts = [f"Total Score: {score:.2f} points"]
        
        # Genre match explanation
        if song.genre.lower() == user.favorite_genre.lower():
            explanation_parts.append(f"✓ +2.0 Genre match ({song.genre})")
        else:
            explanation_parts.append(f"✗ Genre mismatch (song: {song.genre}, user preference: {user.favorite_genre})")
        
        # Mood match explanation
        if song.mood.lower() == user.favorite_mood.lower():
            explanation_parts.append(f"✓ +1.0 Mood match ({song.mood})")
        else:
            explanation_parts.append(f"✗ Mood mismatch (song: {song.mood}, user preference: {user.favorite_mood})")
        
        # Energy similarity explanation (Euclidean distance)
        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        energy_diff = abs(user.target_energy - song.energy)
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy similarity (user: {user.target_energy:.2f}, song: {song.energy:.2f}, difference: {energy_diff:.2f})")
        
        return "\n".join(explanation_parts)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and convert numeric columns to appropriate types."""
    import csv
    
    songs = []
    # Define which columns should be converted to float
    float_columns = {'energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness'}
    # Define which columns should be converted to int
    int_columns = {'id'}
    
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
    """Recommend songs using functional approach with point-weighting scoring and explanations.
    
    Scoring breakdown:
    +2.0 points for genre match
    +1.0 point for mood match
    +0.0 to 1.0 points for energy similarity (Euclidean distance)
    
    Args:
        user_prefs: Dict with keys 'favorite_genre', 'favorite_mood', 'target_energy'
        songs: List of song dictionaries
        k: Number of recommendations to return
    
    Returns:
        List of tuples: (song_dict, score, explanation)
    """
    scored_songs = []
    
    for song in songs:
        score = 0.0
        explanation_parts = []
        
        # +2.0 points for genre match
        if song['genre'].lower() == user_prefs['favorite_genre'].lower():
            score += 2.0
            explanation_parts.append(f"✓ +2.0 Genre match ({song['genre']})")
        else:
            explanation_parts.append(f"✗ Genre mismatch (song: {song['genre']}, preference: {user_prefs['favorite_genre']})")
        
        # +1.0 point for mood match
        if song['mood'].lower() == user_prefs['favorite_mood'].lower():
            score += 1.0
            explanation_parts.append(f"✓ +1.0 Mood match ({song['mood']})")
        else:
            explanation_parts.append(f"✗ Mood mismatch (song: {song['mood']}, preference: {user_prefs['favorite_mood']})")
        
        # Energy similarity: Euclidean distance (0.0 to 1.0 points)
        energy_similarity = 1.0 - abs(user_prefs['target_energy'] - song['energy'])
        energy_diff = abs(user_prefs['target_energy'] - song['energy'])
        score += energy_similarity
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy similarity (user: {user_prefs['target_energy']:.2f}, song: {song['energy']:.2f}, difference: {energy_diff:.2f})")
        
        explanation = f"Total: {score:.2f} points\n" + "\n".join(explanation_parts)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending, then by title for tie-breaking
    scored_songs.sort(key=lambda x: (-x[1], x[0]['title']))
    
    # Return top k songs
    return scored_songs[:k]
