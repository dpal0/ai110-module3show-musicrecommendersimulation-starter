"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def run_profile(profile_name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    print(f"\n{'-'*60}")
    print(f"PROFILE: {profile_name}")
    print(f"{'-'*60}")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"  {i}. [{score:.2f}] {song['title']} — {song['artist']} ({song['genre']}/{song['mood']})")
        print(f"       {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")

    # ── Standard Profiles ──────────────────────────────────────────────────────

    high_energy_pop = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "target_valence": 0.85,
        "target_danceability": 0.85,
        "likes_acoustic": False,
    }

    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "target_valence": 0.55,
        "target_danceability": 0.55,
        "likes_acoustic": True,
    }

    deep_intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "target_valence": 0.30,
        "target_danceability": 0.60,
        "likes_acoustic": False,
    }

    # ── Adversarial / Edge-Case Profiles ───────────────────────────────────────

    # Conflicting preferences: high energy but sad/acoustic — can the scorer handle it?
    conflicting_prefs = {
        "genre": "classical",
        "mood": "sad",
        "energy": 0.90,          # high energy ...
        "target_valence": 0.10,
        "target_danceability": 0.20,
        "likes_acoustic": True,   # ... but wants acoustic
    }

    # Unknown genre & mood: nothing should match on genre/mood, score should rely on energy
    unknown_genre_mood = {
        "genre": "bossa-nova",    # not in dataset
        "mood": "dreamy",         # not in dataset
        "energy": 0.50,
        "target_valence": 0.50,
        "target_danceability": 0.50,
        "likes_acoustic": False,
    }

    # Extreme boundary: energy = 0.0 — pushes nearly every song outside the energy window
    extreme_low_energy = {
        "genre": "ambient",
        "mood": "chill",
        "energy": 0.0,
        "target_valence": 0.60,
        "target_danceability": 0.40,
        "likes_acoustic": True,
    }

    profiles = [
        ("High-Energy Pop",              high_energy_pop),
        ("Chill Lofi",                   chill_lofi),
        ("Deep Intense Rock",            deep_intense_rock),
        ("Adversarial: Conflicting Prefs (high energy + sad + acoustic)", conflicting_prefs),
        ("Adversarial: Unknown Genre & Mood",                              unknown_genre_mood),
        ("Adversarial: Extreme Low Energy (0.0)",                          extreme_low_energy),
    ]

    for name, prefs in profiles:
        run_profile(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
