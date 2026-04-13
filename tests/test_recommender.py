from src.recommender import Song, UserProfile, Recommender, load_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_load_songs_from_csv():
    """Test that load_songs correctly loads songs from the CSV file."""
    songs = load_songs("data/songs.csv")
    
    # Check that songs were loaded
    assert len(songs) > 0, "No songs were loaded from CSV"
    
    # Check first song structure
    first_song = songs[0]
    assert "id" in first_song
    assert "title" in first_song
    assert "artist" in first_song
    assert "genre" in first_song
    assert "mood" in first_song
    
    # Check data types
    assert isinstance(first_song["id"], int), "Song ID should be an integer"
    assert isinstance(first_song["title"], str), "Song title should be a string"
    assert isinstance(first_song["energy"], float), "Energy should be a float"
    assert isinstance(first_song["tempo_bpm"], float), "Tempo should be a float"
    
    # Verify specific song (first row should be "Sunrise City")
    assert first_song["title"] == "Sunrise City"
    assert first_song["artist"] == "Neon Echo"
    assert first_song["genre"] == "pop"
