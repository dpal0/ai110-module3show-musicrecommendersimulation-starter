# Model Card: Music Recommender Simulation

## 1. Model Name

**StillBetterThanSpotify**

---

## 2. Intended Use

StillBetterThanSpotify recommends songs from a small catalog based on a user's stated mood, genre, and energy preferences. It is designed for classroom exploration — not a production app. It assumes the user can describe their taste numerically (e.g., energy level from 0 to 1) and that a single fixed profile captures their current listening mood. It should not be used to make real editorial decisions or personalize music for real users at scale.

---

## 3. How the Model Works

Each song in the catalog has several attributes: genre, mood, energy level, danceability, valence (positivity), and acousticness. The user provides their preferences for each of these.

The system scores every song against those preferences and returns the top five. The scoring works like a weighted checklist:

- **Energy** gets the most weight (35%). If a song's energy is close to your target, it scores well. If it's too far off, it scores zero on this dimension.
- **Mood** (20%) and **Genre** (15%) are all-or-nothing — an exact match scores full points, anything else scores nothing.
- **Artist preference** (10%) rewards songs by artists the user has flagged as favorites; if the user has no preference, every artist gets a neutral half-credit.
- **Valence**, **acousticness**, and **danceability** make up the remaining 20%, using the same proximity logic as energy.

The final score is a weighted sum of all these components. The song with the highest total wins.

---

## 4. Data

The catalog contains 18 songs. Each song has 10 attributes: id, title, artist, genre, mood, energy, tempo (BPM), valence, danceability, and acousticness.

The genres represented are: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, r&b, metal, country, electronic, folk, and soul. Moods include: happy, chill, intense, relaxed, focused, moody, melancholic, sad, romantic, angry, nostalgic, euphoric, and bittersweet.

No data was added or removed from the starter dataset. The catalog is very small — 18 songs cannot represent the full range of human musical taste. Many genres (e.g., reggae, latin, blues) and moods are completely absent, and most moods appear only once, which creates scoring imbalances for users with rare preferences.

---

## 5. Strengths

The system works well when the user's preferences align with the most common patterns in the catalog. The Chill Lofi profile returned all three lofi songs at the top with high confidence, and the Deep Intense Rock profile correctly identified the single song that matched genre, mood, and energy simultaneously as the clear winner (score 0.86).

The weighted design means no single signal dominates unfairly — a song that partially matches on three dimensions can beat one that perfectly matches only one. The system also degrades gracefully when given genres or moods it has never seen: it falls back to energy, valence, and danceability proximity rather than failing entirely.

---

## 6. Limitations and Bias

The system struggles when user preferences conflict with each other or when the catalog has thin coverage.

**Mood Scarcity Bias:** The scoring system awards mood matches in a strict all-or-nothing fashion — a song either perfectly matches the user's favorite mood and earns the full 0.20 weight, or receives nothing. Because the catalog contains only 18 songs and several moods (such as "angry," "nostalgic," "euphoric," and "bittersweet") appear exactly once, a user whose preferred mood is rare will always see that single matching song land near the top of their recommendations, regardless of how poorly it fits on energy, genre, or any other dimension. By contrast, users who prefer "chill" have three candidates competing for that bonus, which produces more varied and arguably fairer results. This imbalance means the recommender does not treat all users equally — rare-mood users are essentially locked into a predetermined top result — and the problem would only worsen if the catalog grew unevenly or if new moods were added without sufficient coverage.

**Conflicting preferences:** When a user asks for contradictory things (e.g., high energy but sad and acoustic), the system does not detect the conflict — it just adds up the partial scores. The result can be counterintuitive: a quiet classical piece can beat every high-energy song because its mood and genre bonuses outweigh the energy mismatch.

**No context awareness:** The system has no memory. It cannot model listening history, time of day, or shifting moods. Every recommendation starts from scratch.

---

## 7. Evaluation

Six user profiles were tested: three standard profiles (High-Energy Pop, Chill Lofi, and Deep Intense Rock) and three adversarial edge cases (Conflicting Preferences, Unknown Genre & Mood, and Extreme Low Energy).

For the standard profiles, the results matched intuition well. The Chill Lofi profile returned all three lofi songs in the top three slots with high confidence scores, and the Deep Intense Rock profile correctly ranked Storm Runner — the only song matching genre, mood, and energy simultaneously — far ahead of everything else at 0.86. The High-Energy Pop profile also behaved as expected, with Sunrise City earning a strong 0.83 by hitting all three major signals.

The most surprising result came from the Conflicting Preferences profile, which asked for high energy (0.90) but also sad mood, acoustic sound, and classical genre. The top result was Adagio in Blue — a slow, quiet classical piece with energy of only 0.19 — because its mood, genre, and acoustic bonuses combined (0.55 total) still beat every high-energy song that matched nothing else. This revealed that when preferences contradict each other, the system quietly favors categorical matches (genre, mood) over the numerically dominant energy score, which can produce counterintuitive results.

The Unknown Genre & Mood profile (bossa-nova / dreamy, neither in the dataset) confirmed the system degrades gracefully — it fell back to energy, valence, and danceability proximity, returning a tightly bunched set of scores between 0.40 and 0.48 with no clear winner. The Extreme Low Energy profile (target 0.0) showed only one song (Spacewalk Thoughts, energy 0.28) within the scoring window, which dominated the top slot at 0.60 while everything else dropped steeply — confirming energy acts as a soft gating mechanism at the extremes.

---

## 8. Future Work

- **Soft mood matching:** Replace the all-or-nothing mood score with a similarity scale (e.g., "intense" and "angry" are closer than "intense" and "chill"). This would reduce the scarcity bias and produce smoother rankings.
- **Conflict detection:** Before scoring, check whether the user's preferences are internally contradictory (e.g., high energy + acoustic + sad) and warn the user or ask a clarifying question.
- **Catalog diversity:** Expand the dataset to include at least 3–5 songs per mood and genre so that categorical matches are always competitive rather than automatic winners.

---

## 9. Personal Reflection

Building this recommender made it clear how much a simple weighted formula can get right — and how quickly it breaks down at the edges. The stress tests were the most valuable part: running the adversarial profiles revealed failure modes (like the conflicting-preferences bug) that would never show up in a happy-path demo. It also changed how I think about real apps like Spotify — their "Discover Weekly" must do a lot of work to handle the cases where user taste is contradictory or underrepresented in the catalog, because a naive scoring approach exposes those gaps immediately.
