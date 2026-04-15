"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender with different scoring strategies.

You can switch between strategies by passing the strategy name when calling the recommendation function.
Available strategies: balanced, genre-first, popularity-first, vibe-mode
"""

from .recommender import Song, UserProfile, Recommender, load_songs
from .scoring_strategies import AVAILABLE_STRATEGIES, get_strategy
from tabulate import tabulate
import csv


# User Preference Profiles
USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "peaceful",
        "target_energy": 0.3,
        "likes_acoustic": True
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.85,
        "likes_acoustic": False
    },
    # Adversarial/Edge Case Profiles
    "Sad Party Animal": {  # Conflicting: high energy but sad mood
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.95,
        "likes_acoustic": False
    },
    "Mellow Intensity": {  # Conflicting: low energy but intense mood
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.1,
        "likes_acoustic": True
    },
    "Acoustic Rave": {  # Conflicting: acoustic preference with extreme energy
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.98,
        "likes_acoustic": True
    },
    "Silent Chaos": {  # Extreme low energy with chaotic mood
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.0,
        "likes_acoustic": True
    },
    "Neutral Entity": {  # Middle ground on everything
        "favorite_genre": "pop",
        "favorite_mood": "peaceful",
        "target_energy": 0.5,
        "likes_acoustic": False
    }
}


def load_songs_oop(csv_path: str) -> list[Song]:
    """
    Load songs from CSV and convert to Song objects (OOP approach).
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of Song objects
    """
    songs = []
    float_columns = {'energy', 'tempo_bpm', 'valence', 'danceability', 'acousticness',
                     'popularity_score', 'artist_followers', 'spotify_streams', 'radio_friendly'}
    int_columns = {'id', 'year_released', 'explicit_content'}
    
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            for col in float_columns:
                row[col] = float(row[col])
            for col in int_columns:
                row[col] = int(row[col])
            
            song = Song(
                id=row['id'],
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                mood=row['mood'],
                energy=row['energy'],
                tempo_bpm=row['tempo_bpm'],
                valence=row['valence'],
                danceability=row['danceability'],
                acousticness=row['acousticness'],
                year_released=row['year_released'],
                popularity_score=row['popularity_score'],
                explicit_content=row['explicit_content'],
                artist_followers=row['artist_followers'],
                spotify_streams=row['spotify_streams'],
                radio_friendly=row['radio_friendly']
            )
            songs.append(song)
    
    print(f"✓ Loaded {len(songs)} songs from {csv_path}")
    return songs


def main(strategy_name: str = "balanced") -> None:
    """
    Main function to run recommendations with a specific strategy.
    
    Args:
        strategy_name: Name of the strategy to use (default: "balanced")
                      Options: balanced, genre-first, popularity-first, vibe-mode
    """
    # Validate and load strategy
    if strategy_name.lower() not in AVAILABLE_STRATEGIES:
        available = ", ".join(AVAILABLE_STRATEGIES.keys())
        print(f"❌ Unknown strategy: {strategy_name}")
        print(f"📋 Available strategies: {available}")
        return
    
    strategy = get_strategy(strategy_name)
    print(f"\n🎯 Using strategy: {strategy_name.upper()}")
    print("=" * 70)
    
    # Load songs and create recommender
    songs = load_songs_oop("data/songs.csv")
    recommender = Recommender(songs, strategy=strategy)
    
    for profile_name, user_prefs in USER_PROFILES.items():
        # Create UserProfile
        user = UserProfile(
            favorite_genre=user_prefs['favorite_genre'],
            favorite_mood=user_prefs['favorite_mood'],
            target_energy=user_prefs['target_energy'],
            likes_acoustic=user_prefs['likes_acoustic']
        )
        
        # Get recommendations
        recommendations = recommender.recommend(user, k=5)
        
        print("\n" + "=" * 100)
        print(f"🎵 {profile_name.upper()} 🎵".center(100))
        print("=" * 100)
        print(f"Preferences: Genre={user.favorite_genre}, Mood={user.favorite_mood}, Energy={user.target_energy:.1f}")
        print(f"Strategy: {recommender.get_strategy_name()}")
        print("=" * 100 + "\n")
        
        # Build table data
        table_data = []
        for rank, song in enumerate(recommendations, 1):
            score = recommender.score_song(user, song)
            explanation = recommender.explain_recommendation(user, song)
            
            # Extract the key reason from the explanation (first line has the score)
            # Get all lines except the first (which is the total score line)
            reason_lines = explanation.split("\n")[1:]
            reason = "\n".join(reason_lines) if reason_lines else explanation
            
            table_data.append([
                rank,
                song.title[:30],  # Truncate title for readability
                song.artist[:20],  # Truncate artist for readability
                song.genre,
                f"{score:.2f}",
                reason
            ])
        
        # Print formatted table
        headers = ["#", "Song", "Artist", "Genre", "Score", "Reasons"]
        print(tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[3, 30, 20, 10, 7, 40]))
        print("\n" + "=" * 100)


def demonstrate_diversity() -> None:
    """
    Demonstrate the diversity and fairness feature.
    Shows how enabling diversity prevents too many songs from the same artist/genre.
    """
    print("\n🎨 DIVERSITY & FAIRNESS DEMONSTRATION")
    print("=" * 70)
    
    # Load songs
    songs = load_songs_oop("data/songs.csv")
    
    # Define a test user profile
    test_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False
    )
    
    print(f"Test User: {test_user.favorite_genre} / {test_user.favorite_mood} / Energy: {test_user.target_energy}")
    print("\n📋 Showing TOP 10 recommendations to highlight diversity benefits\n")
    print("=" * 70)
    
    # WITHOUT diversity
    print("\n❌ WITHOUT DIVERSITY PENALTIES (Original behavior)")
    print("-" * 70)
    recommender_no_diversity = Recommender(songs, strategy=get_strategy("balanced"), enable_diversity=False)
    recommendations_no_div = recommender_no_diversity.recommend(test_user, k=10)
    
    artist_counts = {}
    genre_counts = {}
    for rank, song in enumerate(recommendations_no_div, 1):
        score = recommender_no_diversity.score_song(test_user, song)
        artist_counts[song.artist] = artist_counts.get(song.artist, 0) + 1
        genre_counts[song.genre] = genre_counts.get(song.genre, 0) + 1
        print(f"  #{rank:2d} - {song.title[:40]:40s} | {song.artist[:20]:20s} | {song.genre:10s} | Score: {score:.2f}")
    
    print(f"\n  Artist Distribution (WITHOUT diversity): {dict(sorted(artist_counts.items(), key=lambda x: -x[1]))}")
    print(f"  Genre Distribution (WITHOUT diversity):  {dict(sorted(genre_counts.items(), key=lambda x: -x[1]))}")
    
    # WITH diversity
    print("\n\n✅ WITH DIVERSITY PENALTIES (New fairness feature)")
    print("-" * 70)
    recommender_with_diversity = Recommender(songs, strategy=get_strategy("balanced"), enable_diversity=True)
    recommendations_with_div = recommender_with_diversity.recommend(test_user, k=10)
    
    artist_counts_div = {}
    genre_counts_div = {}
    for rank, song in enumerate(recommendations_with_div, 1):
        score = recommender_with_diversity.score_song(test_user, song)
        # Calculate the penalties applied at this position
        diversity_penalty = recommender_with_diversity._get_diversity_penalty(song, recommendations_with_div[:rank-1])
        
        artist_counts_div[song.artist] = artist_counts_div.get(song.artist, 0) + 1
        genre_counts_div[song.genre] = genre_counts_div.get(song.genre, 0) + 1
        
        penalty_display = f" (Penalty: {diversity_penalty:.1f})" if diversity_penalty < 0 else ""
        print(f"  #{rank:2d} - {song.title[:40]:40s} | {song.artist[:20]:20s} | {song.genre:10s} | Score: {score:.2f}{penalty_display}")
    
    print(f"\n  Artist Distribution (WITH diversity):    {dict(sorted(artist_counts_div.items(), key=lambda x: -x[1]))}")
    print(f"  Genre Distribution (WITH diversity):     {dict(sorted(genre_counts_div.items(), key=lambda x: -x[1]))}")
    
    # Show key differences
    print("\n" + "=" * 70)
    print("📊 KEY INSIGHTS:")
    print("=" * 70)
    
    # Check if diversity made a difference
    genre_change = False
    for genre in set(list(genre_counts.keys()) + list(genre_counts_div.keys())):
        if genre_counts.get(genre, 0) != genre_counts_div.get(genre, 0):
            genre_change = True
            break
    
    if genre_change:
        print("✓ Diversity penalties successfully shifted recommendations!")
        print("  Songs were reranked to promote variety while maintaining relevance.")
        print("\n  Changes detected in genre distribution between with/without diversity.")
    else:
        print("ℹ In this case, the results are very similar (good initial diversity).")
    
    print("\nHow it works: During the selection process, each song gets a diversity penalty")
    print("applied based on how many songs from its artist/genre are already selected.")
    print("This encourages the recommender to include variety while still prioritizing relevance.")
    
    print("\n" + "=" * 70)
    print("📊 DIVERSITY PENALTY RULES:")
    print("=" * 70)
    print("🎤 ARTIST PENALTIES (encouraging artist diversity):")
    print("   • 1st song from artist: No penalty")
    print("   • 2nd song from artist: -0.5 penalty")
    print("   • 3rd song from artist: -1.5 penalty")
    print("   • 4th+ songs from artist: -3.0 penalty")
    print("\n🎵 GENRE PENALTIES (encouraging gentle genre diversity):")
    print("   • 1st song from genre: No penalty")
    print("   • 2nd song from genre: -0.3 penalty")
    print("   • 3rd+ songs from genre: -0.8 penalty")
    print("\nThese penalties are applied to the base score, ensuring relevance is maintained")
    print("(mood, energy, valence matches are still honored) while promoting fair")
    print("representation in recommendations.")
    print("=" * 70)


def compare_strategies() -> None:
    """
    Compare all available strategies for a sample user profile.
    Shows how different strategies rank the same songs differently.
    """
    print("\n🔄 COMPARING ALL STRATEGIES")
    print("=" * 70)
    
    # Load songs
    songs = load_songs_oop("data/songs.csv")
    
    # Define a test user profile
    test_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False
    )
    
    print(f"Test User: {test_user.favorite_genre} / {test_user.favorite_mood} / Energy: {test_user.target_energy}")
    print("=" * 70)
    
    # Test each strategy
    for strategy_name in AVAILABLE_STRATEGIES.keys():
        strategy = get_strategy(strategy_name)
        recommender = Recommender(songs, strategy=strategy)
        recommendations = recommender.recommend(test_user, k=3)
        
        print(f"\n📌 Strategy: {strategy_name.upper()}")
        print("-" * 70)
        for rank, song in enumerate(recommendations, 1):
            score = recommender.score_song(test_user, song)
            print(f"  #{rank} - {song.title} by {song.artist} (Score: {score:.2f})")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "compare":
        # Run comparison mode
        compare_strategies()
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "diversity":
        # Run diversity demonstration
        demonstrate_diversity()
    elif len(sys.argv) > 1:
        # Run with specified strategy
        strategy = sys.argv[1].lower()
        main(strategy)
    else:
        # Run with default strategy
        main()
