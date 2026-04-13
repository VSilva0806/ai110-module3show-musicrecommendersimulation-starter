"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 70)
    print("🎵 TOP MUSIC RECOMMENDATIONS 🎵".center(70))
    print("=" * 70 + "\n")
    
    for rank, rec in enumerate(recommendations, 1):
        # Unpack: (song, score, explanation)
        song, score, explanation = rec
        print(f"#{rank} - {song['title']}")
        print(f"    Score: {score:.2f} points")
        print(f"    Reasons:")
        for line in explanation.split("\n"):
            print(f"      {line}")
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
