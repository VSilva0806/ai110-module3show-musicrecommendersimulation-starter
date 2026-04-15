"""
Scoring Strategies for the Music Recommender System.

This module implements different ranking techniques using the Strategy pattern.
Each strategy defines a different approach to scoring songs based on user preferences.
"""

from abc import ABC, abstractmethod
from typing import List
from .recommender import Song, UserProfile


class ScoringStrategy(ABC):
    """Abstract base class for all scoring strategies."""
    
    @abstractmethod
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score a song based on the strategy's logic."""
        pass
    
    @abstractmethod
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Provide explanation for the score."""
        pass


class BalancedStrategy(ScoringStrategy):
    """
    Default balanced strategy: considers all factors equally.
    
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
    """
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score a song using balanced multi-factor analysis."""
        score = 0.0
        
        # === CORE CONTENT MATCHING (BASELINE) ===
        # +1.0 point for genre match
        if song.genre.lower() == user.favorite_genre.lower():
            score += 1.0
        
        # +2.0 points for mood match
        if song.mood.lower() == user.favorite_mood.lower():
            score += 2.0
        
        # Energy similarity: Euclidean distance (0.0 to 1.0 points)
        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        score += energy_similarity
        
        # === ERA-BASED SCORING ===
        current_year = 2024
        if user.prefers_modern:
            if song.year_released >= 2015:
                era_bonus = min(1.0, 0.8 * (1 - (song.year_released - 2015) / 50))
            else:
                era_bonus = max(0.0, 0.3 - (2015 - song.year_released) / 100)
        else:
            if song.year_released < 2015:
                era_bonus = min(1.0, 0.8 * (1 - (2024 - song.year_released) / 100))
            else:
                era_bonus = max(0.0, 0.3 - (song.year_released - 2015) / 100)
        
        score += era_bonus
        
        # === POPULARITY & CREDIBILITY SCORING ===
        popularity_boost = (song.popularity_score / 100.0) * 0.5
        score += popularity_boost
        
        if song.popularity_score < user.minimum_popularity:
            score -= 0.3
        
        artist_credibility = 0.0
        if user.values_artist_credibility:
            normalized_followers = min(1.0, song.artist_followers / 5000.0)
            artist_credibility = normalized_followers * 0.3
            score += artist_credibility
        
        stream_score = min(0.4, (song.spotify_streams / 700.0) * 0.4)
        score += stream_score
        
        # === RADIO COMPATIBILITY & EXPLICIT CONTENT ===
        radio_friendly_bonus = song.radio_friendly * 0.3
        score += radio_friendly_bonus
        
        if song.explicit_content == 1 and not user.explicit_tolerance:
            score -= 1.0
        
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Explain the balanced score calculation."""
        score = self.score_song(user, song)
        explanation_parts = [f"Total Score: {score:.2f} points (Balanced Strategy)"]
        
        if song.genre.lower() == user.favorite_genre.lower():
            explanation_parts.append(f"✓ +1.0 Genre match ({song.genre})")
        else:
            explanation_parts.append(f"✗ Genre mismatch (song: {song.genre}, preference: {user.favorite_genre})")
        
        if song.mood.lower() == user.favorite_mood.lower():
            explanation_parts.append(f"✓ +2.0 Mood match ({song.mood})")
        else:
            explanation_parts.append(f"✗ Mood mismatch (song: {song.mood}, preference: {user.favorite_mood})")
        
        energy_similarity = 1.0 - abs(user.target_energy - song.energy)
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy similarity")
        
        current_year = 2024
        if user.prefers_modern:
            if song.year_released >= 2015:
                era_bonus = min(1.0, 0.8 * (1 - (song.year_released - 2015) / 50))
            else:
                era_bonus = max(0.0, 0.3 - (2015 - song.year_released) / 100)
        else:
            if song.year_released < 2015:
                era_bonus = min(1.0, 0.8 * (1 - (2024 - song.year_released) / 100))
            else:
                era_bonus = max(0.0, 0.3 - (song.year_released - 2015) / 100)
        explanation_parts.append(f"✓ +{era_bonus:.2f} Era preference")
        
        return "\n".join(explanation_parts)


class GenreFirstStrategy(ScoringStrategy):
    """
    Genre-first strategy: heavily prioritizes genre matching above all else.
    
    Scoring:
    +5.0 points for genre match (primary focus)
    +1.0 points for mood match
    +0.2 to 0.3 points for energy similarity (reduced weight)
    +0.2 to 0.3 points for popularity (minimal weight)
    """
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score emphasizing genre matching."""
        score = 0.0
        
        # === GENRE PRIMARY SCORING ===
        # +5.0 massive boost for genre match
        if song.genre.lower() == user.favorite_genre.lower():
            score += 5.0
        else:
            # Penalty for genre mismatch
            score -= 2.0
        
        # +1.0 points for mood match (secondary)
        if song.mood.lower() == user.favorite_mood.lower():
            score += 1.0
        
        # Energy similarity: minimal weight (0.2 to 0.3 points)
        energy_similarity = (1.0 - abs(user.target_energy - song.energy)) * 0.3
        score += energy_similarity
        
        # Popularity: minimal weight (0.2 to 0.3 points)
        popularity_boost = (song.popularity_score / 100.0) * 0.3
        score += popularity_boost
        
        # Explicit content penalty
        if song.explicit_content == 1 and not user.explicit_tolerance:
            score -= 1.5
        
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Explain the genre-first score."""
        score = self.score_song(user, song)
        explanation_parts = [f"Total Score: {score:.2f} points (Genre-First Strategy)"]
        explanation_parts.append("⚠️  This strategy PRIORITIZES genre matching!")
        
        if song.genre.lower() == user.favorite_genre.lower():
            explanation_parts.append(f"✓ +5.0 STRONG Genre match ({song.genre})")
        else:
            explanation_parts.append(f"✗ -2.0 Genre mismatch (song: {song.genre}, preference: {user.favorite_genre})")
        
        if song.mood.lower() == user.favorite_mood.lower():
            explanation_parts.append(f"✓ +1.0 Mood match ({song.mood})")
        
        energy_similarity = (1.0 - abs(user.target_energy - song.energy)) * 0.3
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy (minimal weight)")
        
        return "\n".join(explanation_parts)


class PopularityFirstStrategy(ScoringStrategy):
    """
    Popularity-first strategy: prioritizes streaming popularity and artist credibility.
    
    Scoring:
    +0.5 to 0.6 points for popularity score (high weight)
    +0.4 to 0.5 points for streaming popularity (high weight)
    +0.3 to 0.4 points for artist credibility (high weight)
    +0.5 for genre match
    +0.5 for mood match
    """
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score emphasizing popularity metrics."""
        score = 0.0
        
        # === POPULARITY PRIMARY SCORING ===
        # Heavy weight on popularity score (0.5 to 1.0 points)
        popularity_boost = (song.popularity_score / 100.0) * 1.0
        score += popularity_boost
        
        # Heavy weight on streaming popularity (0.4 to 1.0 points)
        stream_score = min(1.0, (song.spotify_streams / 700.0) * 1.0)
        score += stream_score
        
        # Heavy weight on artist credibility (0.3 to 0.6 points)
        if user.values_artist_credibility:
            normalized_followers = min(1.0, song.artist_followers / 5000.0)
            artist_credibility = normalized_followers * 0.6
            score += artist_credibility
        
        # Light weight on content matching
        if song.genre.lower() == user.favorite_genre.lower():
            score += 0.5
        
        if song.mood.lower() == user.favorite_mood.lower():
            score += 0.5
        
        # Explicit content penalty
        if song.explicit_content == 1 and not user.explicit_tolerance:
            score -= 0.5
        
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Explain the popularity-first score."""
        score = self.score_song(user, song)
        explanation_parts = [f"Total Score: {score:.2f} points (Popularity-First Strategy)"]
        explanation_parts.append("📊 This strategy PRIORITIZES popularity metrics!")
        
        popularity_boost = (song.popularity_score / 100.0) * 1.0
        explanation_parts.append(f"✓ +{popularity_boost:.2f} Popularity score ({song.popularity_score}/100)")
        
        stream_score = min(1.0, (song.spotify_streams / 700.0) * 1.0)
        explanation_parts.append(f"✓ +{stream_score:.2f} Streaming popularity ({song.spotify_streams}M streams)")
        
        if user.values_artist_credibility:
            normalized_followers = min(1.0, song.artist_followers / 5000.0)
            artist_credibility = normalized_followers * 0.6
            explanation_parts.append(f"✓ +{artist_credibility:.2f} Artist credibility ({song.artist_followers}k followers)")
        
        return "\n".join(explanation_parts)


class VibeModeStrategy(ScoringStrategy):
    """
    Vibe-mode strategy: prioritizes mood and energy matching for perfect listening experience.
    
    Scoring:
    +3.0 points for mood match (primary)
    +1.0 to 2.0 points for energy similarity (high weight)
    +0.5 points for genre match
    +0.2 for popularity (minimal weight)
    """
    
    def score_song(self, user: UserProfile, song: Song) -> float:
        """Score emphasizing mood and energy vibes."""
        score = 0.0
        
        # === VIBE PRIMARY SCORING ===
        # +3.0 for mood match
        if song.mood.lower() == user.favorite_mood.lower():
            score += 3.0
        
        # Energy similarity: heavy weight (1.0 to 2.0 points)
        energy_similarity = (1.0 - abs(user.target_energy - song.energy)) * 2.0
        score += energy_similarity
        
        # Genre match: secondary (0.5 points)
        if song.genre.lower() == user.favorite_genre.lower():
            score += 0.5
        
        # Acoustic preference
        if user.likes_acoustic and song.acousticness > 0.7:
            score += 0.5
        elif not user.likes_acoustic and song.acousticness < 0.3:
            score += 0.3
        
        # Minimal popularity weight
        popularity_boost = (song.popularity_score / 100.0) * 0.2
        score += popularity_boost
        
        # Explicit content penalty
        if song.explicit_content == 1 and not user.explicit_tolerance:
            score -= 0.8
        
        return max(0.0, score)
    
    def explain_score(self, user: UserProfile, song: Song) -> str:
        """Explain the vibe-mode score."""
        score = self.score_song(user, song)
        explanation_parts = [f"Total Score: {score:.2f} points (Vibe-Mode Strategy)"]
        explanation_parts.append("🎵 This strategy prioritizes MOOD and ENERGY!")
        
        if song.mood.lower() == user.favorite_mood.lower():
            explanation_parts.append(f"✓ +3.0 Perfect mood match ({song.mood})")
        
        energy_similarity = (1.0 - abs(user.target_energy - song.energy)) * 2.0
        explanation_parts.append(f"✓ +{energy_similarity:.2f} Energy perfect fit (user: {user.target_energy:.2f}, song: {song.energy:.2f})")
        
        if user.likes_acoustic:
            explanation_parts.append(f"  Acoustic preference: {song.acousticness:.2f}")
        
        return "\n".join(explanation_parts)


# Strategy registry for easy lookup
AVAILABLE_STRATEGIES = {
    "balanced": BalancedStrategy,
    "genre-first": GenreFirstStrategy,
    "popularity-first": PopularityFirstStrategy,
    "vibe-mode": VibeModeStrategy,
}

def get_strategy(strategy_name: str) -> ScoringStrategy:
    """Get a strategy instance by name."""
    strategy_class = AVAILABLE_STRATEGIES.get(strategy_name.lower())
    if strategy_class is None:
        available = ", ".join(AVAILABLE_STRATEGIES.keys())
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {available}")
    return strategy_class()
