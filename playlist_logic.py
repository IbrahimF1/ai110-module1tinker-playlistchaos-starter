"""
Playlist Logic Module
======================
This module provides core functionality for managing and organizing music playlists
based on mood classification, user profiles, and song attributes.

Key Concepts:
- Songs are represented as dictionaries with keys: title, artist, genre, energy, tags
- Playlists are grouped by mood: "Hype", "Chill", and "Mixed"
- User profiles define preferences for mood classification
"""

from typing import Dict, List, Optional, Tuple

# Type aliases for better code readability
# Song: A dictionary representing a single song with metadata
# Example: {"title": "Thunderstruck", "artist": "AC/DC", "genre": "rock", "energy": 9, "tags": ["classic", "guitar"]}
Song = Dict[str, object]

# PlaylistMap: A dictionary mapping mood names to lists of songs
# Example: {"Hype": [song1, song2], "Chill": [song3], "Mixed": [song4]}
PlaylistMap = Dict[str, List[Song]]


# Default user profile configuration
# This profile serves as the baseline for mood classification when no custom profile is provided
DEFAULT_PROFILE = {
    "name": "Default",           # Profile name for identification
    "hype_min_energy": 7,        # Songs with energy >= 7 are classified as "Hype"
    "chill_max_energy": 3,       # Songs with energy <= 3 are classified as "Chill"
    "favorite_genre": "rock",    # Songs in this genre are automatically "Hype"
    "include_mixed": True,       # Whether to include "Mixed" mood playlist in views
}


def normalize_title(title: str) -> str:
    """
    Normalize a song title for consistent comparisons.
    
    This function ensures titles are in a consistent format by:
    1. Checking if the input is a valid string
    2. Removing leading/trailing whitespace
    
    Args:
        title (str): The raw song title to normalize
        
    Returns:
        str: The normalized title (empty string if input is not a valid string)
        
    Example:
        >>> normalize_title("  Thunderstruck  ")
        "Thunderstruck"
        >>> normalize_title(123)
        ""
        >>> normalize_title("")
        ""
    """
    # ❌ DESIGN QUIRK: Only strips whitespace, doesn't convert to lowercase
    # Inconsistent with normalize_artist() which does both strip AND lowercase
    # Guard clause: return empty string if input is not a string type
    if not isinstance(title, str):
        return ""
    # Remove leading and trailing whitespace from the title
    # return title.strip()
    # ✅ FIX: Add lowercase for consistency with normalize_artist()
    return title.strip().lower()


def normalize_artist(artist: str) -> str:
    """
    Normalize an artist name for consistent comparisons.
    
    This function ensures artist names are in a consistent format by:
    1. Checking if the input is falsy (None, empty string, etc.)
    2. Removing leading/trailing whitespace
    3. Converting to lowercase for case-insensitive comparisons
    
    Args:
        artist (str): The raw artist name to normalize
        
    Returns:
        str: The normalized artist name (empty string if input is falsy)
        
    Example:
        >>> normalize_artist("  AC/DC  ")
        "ac/dc"
        >>> normalize_artist("The Weeknd")
        "the weeknd"
        >>> normalize_artist("")
        ""
        >>> normalize_artist(None)
        ""
    """
    # Return empty string if artist is falsy (None, "", 0, False, etc.)
    if not artist:
        return ""
    # Strip whitespace and convert to lowercase for consistent matching
    return artist.strip().lower()


def normalize_genre(genre: str) -> str:
    """
    Normalize a genre name for consistent comparisons.
    
    This function ensures genre names are in a consistent format by:
    1. Removing leading/trailing whitespace
    2. Converting to lowercase for case-insensitive comparisons
    
    Args:
        genre (str): The raw genre name to normalize
        
    Returns:
        str: The normalized genre name in lowercase
        
    Example:
        >>> normalize_genre("  Rock  ")
        "rock"
        >>> normalize_genre("ELECTRONIC")
        "electronic"
        >>> normalize_genre("Lo-Fi")
        "lo-fi"
    """
    # ❌ DESIGN QUIRK: Order is .lower().strip() - strips AFTER lowercasing
    # normalize_title() uses .strip() only - inconsistent order of operations
    # Strip whitespace and convert to lowercase
    # return genre.lower().strip()
    # ✅ FIX: Use .strip().lower() for consistency with normalize_title() (now also lowercases)
    return genre.strip().lower()


def normalize_song(raw: Song) -> Song:
    """
    Normalize a raw song dictionary into a standardized format.
    
    This function processes a raw song dictionary and returns a normalized version
    with all fields in consistent formats. It handles various input types and
    ensures all expected keys are present with proper values.
    
    Args:
        raw (Song): A dictionary containing raw song data with potentially
                    inconsistent formatting or missing keys
                    
    Returns:
        Song: A normalized song dictionary with keys: title, artist, genre, energy, tags
              
    Example:
        >>> normalize_song({"title": "  Song  ", "artist": "Artist", "genre": "Rock", "energy": "8", "tags": "tag1"})
        {"title": "Song", "artist": "artist", "genre": "rock", "energy": 8, "tags": ["tag1"]}
        
        >>> normalize_song({"title": "Test", "artist": "DJ", "genre": "electronic", "energy": "invalid", "tags": ["a", "b"]})
        {"title": "Test", "artist": "dj", "genre": "electronic", "energy": 0, "tags": ["a", "b"]}
    """
    # Normalize string fields using their respective normalization functions
    title = normalize_title(str(raw.get("title", "")))
    artist = normalize_artist(str(raw.get("artist", "")))
    genre = normalize_genre(str(raw.get("genre", "")))
    
    # Get energy value, defaulting to 0 if not present
    energy = raw.get("energy", 0)

    # Handle energy conversion if it's stored as a string
    if isinstance(energy, str):
        try:
            energy = int(energy)  # Try to convert string to integer
        except ValueError:
            energy = 0  # Use 0 if conversion fails

    # Get tags, defaulting to empty list if not present
    tags = raw.get("tags", [])
    # Convert single string tag to list for consistency
    if isinstance(tags, str):
        tags = [tags]

    # Return a new dictionary with all normalized fields
    return {
        "title": title,
        "artist": artist,
        "genre": genre,
        "energy": energy,
        "tags": tags,
    }


def classify_song(song: Song, profile: Dict[str, object]) -> str:
    """
    Classify a song into a mood category based on its attributes and user profile.
    
    This function determines whether a song should be classified as "Hype", "Chill",
    or "Mixed" by evaluating multiple criteria in priority order:
    
    1. Hype criteria (any one triggers "Hype" classification):
       - Song's genre matches the user's favorite genre
       - Song's energy level meets or exceeds the hype_min_energy threshold
       - Song's genre contains hype-related keywords (rock, punk, party)
       
    2. Chill criteria (any one triggers "Chill" classification):
       - Song's energy level is at or below the chill_max_energy threshold
       - Song's title contains chill-related keywords (lofi, ambient, sleep)
       
    3. Default: "Mixed" if neither Hype nor Chill criteria are met
    
    Args:
        song (Song): A normalized song dictionary with keys: title, artist, genre, energy, tags
        profile (Dict[str, object]): User profile containing mood classification preferences
                                     with keys: hype_min_energy, chill_max_energy, favorite_genre
                                     
    Returns:
        str: The mood classification: "Hype", "Chill", or "Mixed"
        
    Example:
        >>> song = {"title": "Thunderstruck", "artist": "ac/dc", "genre": "rock", "energy": 9, "tags": []}
        >>> profile = {"hype_min_energy": 7, "chill_max_energy": 3, "favorite_genre": "rock"}
        >>> classify_song(song, profile)
        "Hype"  # Matches favorite genre
        
        >>> song = {"title": "Lo-fi Rain", "artist": "dj calm", "genre": "lofi", "energy": 2, "tags": []}
        >>> classify_song(song, profile)
        "Chill"  # Energy <= chill_max_energy
        
        >>> song = {"title": "Night Drive", "artist": "neon echo", "genre": "electronic", "energy": 6, "tags": []}
        >>> classify_song(song, profile)
        "Mixed"  # Doesn't meet Hype or Chill criteria
    """
    # Extract song attributes
    # ❌ BUG: energy might be a string or None, not an int
    # energy = song.get("energy", 0)
    # ✅ FIX: Safely convert energy to int
    energy_raw = song.get("energy", 0)
    if isinstance(energy_raw, str):
        try:
            energy = int(energy_raw)
        except ValueError:
            energy = 0
    elif isinstance(energy_raw, (int, float)):
        energy = int(energy_raw)
    else:
        energy = 0

    # ❌ BUG: genre might be None or not a string
    # genre = song.get("genre", "")
    # ✅ FIX: Safely convert genre to string
    genre = str(song.get("genre", "")) if song.get("genre") is not None else ""

    # ❌ BUG: title might be None or not a string
    # title = song.get("title", "")
    # ✅ FIX: Safely convert title to string
    title = str(song.get("title", "")) if song.get("title") is not None else ""

    # Extract profile preferences with defaults
    # ❌ BUG: These values might be strings or None, not the expected types
    # hype_min_energy = profile.get("hype_min_energy", 7)
    # chill_max_energy = profile.get("chill_max_energy", 3)
    # favorite_genre = profile.get("favorite_genre", "")
    # ✅ FIX: Safely convert profile values to expected types
    hype_min_energy_raw = profile.get("hype_min_energy", 7)
    if isinstance(hype_min_energy_raw, str):
        try:
            hype_min_energy = int(hype_min_energy_raw)
        except ValueError:
            hype_min_energy = 7
    elif isinstance(hype_min_energy_raw, (int, float)):
        hype_min_energy = int(hype_min_energy_raw)
    else:
        hype_min_energy = 7

    chill_max_energy_raw = profile.get("chill_max_energy", 3)
    if isinstance(chill_max_energy_raw, str):
        try:
            chill_max_energy = int(chill_max_energy_raw)
        except ValueError:
            chill_max_energy = 3
    elif isinstance(chill_max_energy_raw, (int, float)):
        chill_max_energy = int(chill_max_energy_raw)
    else:
        chill_max_energy = 3

    favorite_genre = str(profile.get("favorite_genre", "")) if profile.get("favorite_genre") is not None else ""

    # Define keyword lists for mood detection
    # Hype keywords in genre that trigger Hype classification
    hype_keywords = ["rock", "punk", "party"]
    # Chill keywords in title that trigger Chill classification
    chill_keywords = ["lofi", "ambient", "sleep"]

    # Check if genre contains any hype keywords (case-insensitive)
    # ❌ BUG: genre might be None or not a string, and this check is CASE-SENSITIVE
    # is_hype_keyword = any(k in genre for k in hype_keywords)
    # ✅ FIX: Ensure genre is a string and lowercase for case-insensitive matching
    genre_str = str(genre).lower() if genre is not None else ""
    is_hype_keyword = any(k in genre_str for k in hype_keywords)
    # ❌ BUG: Comment says "case-insensitive" but this check is CASE-SENSITIVE
    # Title is NOT lowercased (only stripped in normalize_title()), so "Lo-fi" won't match "lofi"
    # Should be: is_chill_keyword = any(k in title.lower() for k in chill_keywords)
    # Check if title contains any chill keywords (case-insensitive)
    # is_chill_keyword = any(k in title for k in chill_keywords)
    # ✅ FIX: Lowercase title for case-insensitive matching (now that normalize_title() lowercases)
    # ❌ BUG: title might be None or not a string, causing .lower() to fail
    # is_chill_keyword = any(k in title.lower() for k in chill_keywords)
    # ✅ FIX: Ensure title is a string before calling .lower()
    title_str = str(title).lower() if title is not None else ""
    is_chill_keyword = any(k in title_str for k in chill_keywords)

    # Hype classification: priority 1
    # Returns "Hype" if ANY of these conditions are true:
    # 1. Genre matches favorite genre exactly
    # 2. Energy meets or exceeds hype threshold
    # 3. Genre contains a hype keyword
    if genre == favorite_genre or energy >= hype_min_energy or is_hype_keyword:
        return "Hype"
    
    # Chill classification: priority 2
    # Returns "Chill" if ANY of these conditions are true:
    # 1. Energy is at or below chill threshold
    # 2. Title contains a chill keyword
    if energy <= chill_max_energy or is_chill_keyword:
        return "Chill"
    
    # Default classification: "Mixed"
    # Used when song doesn't meet Hype or Chill criteria
    return "Mixed"


def build_playlists(songs: List[Song], profile: Dict[str, object]) -> PlaylistMap:
    """
    Group a list of songs into mood-based playlists according to a user profile.
    
    This function processes each song through normalization and classification,
    then organizes them into three playlists: "Hype", "Chill", and "Mixed".
    Each song is assigned its mood classification before being added to the
    appropriate playlist.
    
    Args:
        songs (List[Song]): A list of raw song dictionaries to be organized
        profile (Dict[str, object]): User profile containing mood classification preferences
                                      with keys: hype_min_energy, chill_max_energy, favorite_genre
                                      
    Returns:
        PlaylistMap: A dictionary with mood names as keys and lists of songs as values
                     Format: {"Hype": [songs], "Chill": [songs], "Mixed": [songs]}
                     
    Example:
        >>> songs = [
        ...     {"title": "Thunderstruck", "artist": "AC/DC", "genre": "rock", "energy": 9, "tags": []},
        ...     {"title": "Lo-fi Rain", "artist": "DJ Calm", "genre": "lofi", "energy": 2, "tags": []},
        ...     {"title": "Night Drive", "artist": "Neon Echo", "genre": "electronic", "energy": 6, "tags": []}
        ... ]
        >>> profile = {"hype_min_energy": 7, "chill_max_energy": 3, "favorite_genre": "rock"}
        >>> playlists = build_playlists(songs, profile)
        >>> playlists["Hype"][0]["title"]
        "Thunderstruck"
        >>> playlists["Chill"][0]["title"]
        "Lo-fi Rain"
        >>> playlists["Mixed"][0]["title"]
        "Night Drive"
    """
    # Initialize empty playlists for each mood category
    playlists: PlaylistMap = {
        "Hype": [],
        "Chill": [],
        "Mixed": [],
    }

    # Process each song individually
    for song in songs:
        # Normalize the song data to ensure consistent format
        normalized = normalize_song(song)
        # Classify the song into a mood category based on profile
        mood = classify_song(normalized, profile)
        # Add the mood classification to the song dictionary
        normalized["mood"] = mood
        # Add the song to the appropriate playlist
        playlists[mood].append(normalized)

    # Return the organized playlists
    return playlists


def merge_playlists(a: PlaylistMap, b: PlaylistMap) -> PlaylistMap:
    """
    Merge two playlist maps into a single combined playlist map.
    
    This function combines songs from two PlaylistMap objects. If both maps
    have the same mood key, their song lists are concatenated. If a mood key
    exists in only one map, it's included as-is in the result.
    
    Args:
        a (PlaylistMap): First playlist map to merge
        b (PlaylistMap): Second playlist map to merge
        
    Returns:
        PlaylistMap: A new playlist map containing all songs from both inputs
        
    Example:
        >>> a = {"Hype": [{"title": "Song1"}], "Chill": [{"title": "Song2"}]}
        >>> b = {"Hype": [{"title": "Song3"}], "Mixed": [{"title": "Song4"}]}
        >>> merged = merge_playlists(a, b)
        >>> merged["Hype"]
        [{"title": "Song1"}, {"title": "Song3"}]
        >>> merged["Chill"]
        [{"title": "Song2"}]
        >>> merged["Mixed"]
        [{"title": "Song4"}]
    """
    # Initialize empty merged playlist map
    merged: PlaylistMap = {}
    
    # Get all unique keys from both playlist maps
    # Using set() to avoid duplicates
    all_keys = set(list(a.keys()) + list(b.keys()))
    
    # For each mood key, merge the song lists from both maps
    for key in all_keys:
        # Start with songs from map 'a' (or empty list if key doesn't exist)
        merged[key] = a.get(key, [])
        # Extend with songs from map 'b' (or empty list if key doesn't exist)
        merged[key].extend(b.get(key, []))
    
    return merged


def compute_playlist_stats(playlists: PlaylistMap) -> Dict[str, object]:
    """
    Compute comprehensive statistics across all playlists.
    
    This function calculates various metrics about the songs in all playlists,
    including counts, ratios, averages, and top artist information.
    
    Stats calculated:
    - total_songs: Total number of songs across all playlists
    - hype_count: Number of songs in Hype playlist
    - chill_count: Number of songs in Chill playlist
    - mixed_count: Number of songs in Mixed playlist
    - hype_ratio: Ratio of Hype songs to total songs (0.0 to 1.0)
    - avg_energy: Average energy level across all songs
    - top_artist: The artist with the most songs
    - top_artist_count: Number of songs by the top artist
    
    Args:
        playlists (PlaylistMap): A dictionary mapping mood names to lists of songs
        
    Returns:
        Dict[str, object]: A dictionary containing all computed statistics
        
    Example:
        >>> playlists = {
        ...     "Hype": [{"title": "Song1", "artist": "Artist1", "energy": 8}],
        ...     "Chill": [{"title": "Song2", "artist": "Artist1", "energy": 2}],
        ...     "Mixed": [{"title": "Song3", "artist": "Artist2", "energy": 5}]
        ... }
        >>> stats = compute_playlist_stats(playlists)
        >>> stats["total_songs"]
        3
        >>> stats["hype_count"]
        1
        >>> stats["avg_energy"]
        5.0
        >>> stats["top_artist"]
        "artist1"
    """
    # Collect all songs from all playlists into a single list
    all_songs: List[Song] = []
    for songs in playlists.values():
        all_songs.extend(songs)

    # Extract individual playlists for easier access
    hype = playlists.get("Hype", [])
    chill = playlists.get("Chill", [])
    mixed = playlists.get("Mixed", [])

    # Calculate hype ratio: proportion of Hype songs relative to total
    # ❌ BUG: This uses hype count as BOTH numerator AND denominator
    # Result is always 1.0 (or 0.0 if empty), not the actual ratio
    # Should be: total = len(all_songs); hype_ratio = len(hype) / total if total > 0 else 0.0
    # Note: This uses hype count as denominator, which may be intentional behavior
    # total = len(hype)
    # hype_ratio = len(hype) / total if total > 0 else 0.0
    # ✅ FIX: Use total songs count as denominator for actual ratio
    total = len(all_songs)
    hype_ratio = len(hype) / total if total > 0 else 0.0

    # Calculate average energy across all songs
    avg_energy = 0.0
    if all_songs:
        # ❌ BUG: Only sums energy from Hype playlist, not all songs
        # This gives incorrect average - should sum from all_songs, not just hype
        # Sum energy levels from Hype playlist only (intentional behavior)
        # total_energy = sum(song.get("energy", 0) for song in hype)
        # ✅ FIX: Sum energy from all songs, not just Hype playlist
        # ✅ FIX: Convert energy values to int to resolve type error
        # type: ignore[arg-type] - Song values are object type, but energy is expected to be numeric
        total_energy = sum(int(song.get("energy", 0)) for song in all_songs)  # type: ignore[arg-type]
        # Divide by total songs across all playlists
        avg_energy = total_energy / len(all_songs)

    # Find the most common artist across all songs
    top_artist, top_count = most_common_artist(all_songs)

    # Return all computed statistics in a dictionary
    return {
        "total_songs": len(all_songs),
        "hype_count": len(hype),
        "chill_count": len(chill),
        "mixed_count": len(mixed),
        "hype_ratio": hype_ratio,
        "avg_energy": avg_energy,
        "top_artist": top_artist,
        "top_artist_count": top_count,
    }


def most_common_artist(songs: List[Song]) -> Tuple[str, int]:
    """
    Find the artist with the most songs in a list.
    
    This function counts occurrences of each artist and returns the one
    with the highest count. If there's a tie, the first one encountered
    (after sorting by count) is returned.
    
    Args:
        songs (List[Song]): A list of song dictionaries to analyze
        
    Returns:
        Tuple[str, int]: A tuple containing (artist_name, song_count)
                         Returns ("", 0) if no valid artists are found
                         
    Example:
        >>> songs = [
        ...     {"title": "Song1", "artist": "Artist1"},
        ...     {"title": "Song2", "artist": "Artist1"},
        ...     {"title": "Song3", "artist": "Artist2"}
        ... ]
        >>> most_common_artist(songs)
        ("artist1", 2)
        
        >>> most_common_artist([])
        ("", 0)
    """
    # Initialize empty dictionary to track artist counts
    counts: Dict[str, int] = {}
    
    # Count occurrences of each artist
    for song in songs:
        artist = str(song.get("artist", ""))
        # Skip songs with empty artist names
        if not artist:
            continue
        # Increment count for this artist (initialize to 0 if first occurrence)
        counts[artist] = counts.get(artist, 0) + 1

    # Return empty result if no artists were found
    if not counts:
        return "", 0

    # Sort artists by count in descending order and return the top one
    items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return items[0]


def search_songs(
    songs: List[Song],
    query: str,
    field: str = "artist",
) -> List[Song]:
    """
    Search for songs that match a query string on a specified field.
    
    This function filters a list of songs, returning only those where the
    specified field contains the query string. The search is case-insensitive
    and checks if the field value is a substring of the query (not vice versa).
    
    Note: This implementation checks if the field value is IN the query,
    which is the reverse of typical search behavior (query IN field value).
    
    Args:
        songs (List[Song]): A list of song dictionaries to search
        query (str): The search query string
        field (str): The song field to search within (default: "artist")
        
    Returns:
        List[Song]: A filtered list of songs matching the search criteria
                    Returns all songs if query is empty
                    
    Example:
        >>> songs = [
        ...     {"title": "Song1", "artist": "The Weeknd"},
        ...     {"title": "Song2", "artist": "DJ Calm"},
        ...     {"title": "Song3", "artist": "AC/DC"}
        ... ]
        >>> search_songs(songs, "the weeknd", field="artist")
        [{"title": "Song1", "artist": "The Weeknd"}]
        
        >>> search_songs(songs, "")
        [{"title": "Song1", "artist": "The Weeknd"}, {"title": "Song2", "artist": "DJ Calm"}, {"title": "Song3", "artist": "AC/DC"}]
    """
    # Return all songs if query is empty (no filtering)
    if not query:
        return songs

    # Normalize query: lowercase and strip whitespace
    q = query.lower().strip()
    filtered: List[Song] = []

    # Filter songs based on the query
    for song in songs:
        # Get the field value and convert to lowercase
        value = str(song.get(field, "")).lower()
        # ❌ BUG: This checks if field value is IN query (reverse search)
        # Should be: if value and q in value: (query IN field value)
        # Example: Searching "the weeknd" would match "the" but NOT "weeknd"
        # Check if field value is contained within the query (reverse search)
        # if value and value in q:
        # ✅ FIX: Check if query is IN field value (normal search behavior)
        if value and q in value:
            filtered.append(song)

    return filtered


def lucky_pick(
    playlists: PlaylistMap,
    mode: str = "any",
) -> Optional[Song]:
    """
    Randomly select a song from playlists based on the specified mode.
    
    This function provides a "lucky dip" feature to randomly select a song
    from the available playlists. The mode parameter determines which
    playlists are included in the selection pool.
    
    Modes:
    - "hype": Only selects from the Hype playlist
    - "chill": Only selects from the Chill playlist
    - "any": Selects from both Hype and Chill playlists
    
    Args:
        playlists (PlaylistMap): A dictionary mapping mood names to lists of songs
        mode (str): The selection mode: "hype", "chill", or "any" (default: "any")
        
    Returns:
        Optional[Song]: A randomly selected song, or None if no songs are available
                        in the selected playlist(s)
                        
    Example:
        >>> playlists = {
        ...     "Hype": [{"title": "Song1", "artist": "Artist1"}],
        ...     "Chill": [{"title": "Song2", "artist": "Artist2"}],
        ...     "Mixed": [{"title": "Song3", "artist": "Artist3"}]
        ... }
        >>> lucky_pick(playlists, mode="hype")  # Returns Song1
        {"title": "Song1", "artist": "Artist1", ...}
        >>> lucky_pick(playlists, mode="chill")  # Returns Song2
        {"title": "Song2", "artist": "Artist2", ...}
        >>> lucky_pick(playlists, mode="any")  # Returns Song1 or Song2 randomly
        {"title": "Song1", "artist": "Artist1", ...}  # or Song2
    """
    # Select the appropriate playlist(s) based on mode
    if mode == "hype":
        songs = playlists.get("Hype", [])
    elif mode == "chill":
        songs = playlists.get("Chill", [])
    else:
        # "any" mode: combine Hype and Chill playlists
        songs = playlists.get("Hype", []) + playlists.get("Chill", [])

    # Return a random song from the selected pool
    return random_choice_or_none(songs)


def random_choice_or_none(songs: List[Song]) -> Optional[Song]:
    """
    Return a random song from a list, or None if the list is empty.
    
    This is a helper function that uses Python's random.choice to select
    a random element from the song list. It handles the edge case of
    an empty list by returning None.
    
    Args:
        songs (List[Song]): A list of song dictionaries to choose from
        
    Returns:
        Optional[Song]: A randomly selected song, or None if the list is empty
        
    Example:
        >>> songs = [{"title": "Song1"}, {"title": "Song2"}, {"title": "Song3"}]
        >>> random_choice_or_none(songs)  # Returns one of the three songs randomly
        {"title": "Song2", ...}
        
        >>> random_choice_or_none([])
        None
    """
    import random

    # ❌ DOCSTRING/BEHAVIOR MISMATCH: Docstring says "return None if the list is empty"
    # but the function actually raises IndexError on empty list (random.choice behavior)
    # The comment below acknowledges this but doesn't fix it
    # random.choice raises IndexError on empty list, but we let it propagate
    # The calling function (lucky_pick) should handle empty lists appropriately
    # return random.choice(songs)
    # ✅ FIX: Return None for empty list, matching docstring behavior
    if not songs:
        return None
    return random.choice(songs)


def history_summary(history: List[Song]) -> Dict[str, int]:
    """
    Generate a summary of mood classifications from song history.
    
    This function counts how many songs of each mood (Hype, Chill, Mixed)
    have been selected in the user's pick history. It's useful for
    tracking listening patterns and preferences over time.
    
    Args:
        history (List[Song]): A list of previously picked songs, each with a "mood" key
        
    Returns:
        Dict[str, int]: A dictionary with mood names as keys and counts as values
                        Format: {"Hype": count, "Chill": count, "Mixed": count}
                        
    Example:
        >>> history = [
        ...     {"title": "Song1", "mood": "Hype"},
        ...     {"title": "Song2", "mood": "Chill"},
        ...     {"title": "Song3", "mood": "Hype"},
        ...     {"title": "Song4", "mood": "Mixed"}
        ... ]
        >>> history_summary(history)
        {"Hype": 2, "Chill": 1, "Mixed": 1}
        
        >>> history_summary([])
        {"Hype": 0, "Chill": 0, "Mixed": 0}
    """
    # Initialize counter dictionary for all three moods
    counts = {"Hype": 0, "Chill": 0, "Mixed": 0}
    
    # Count occurrences of each mood in the history
    for song in history:
        mood = str(song.get("mood", "Mixed"))
        # If mood is not one of the expected values, count it as "Mixed"
        if mood not in counts:
            counts["Mixed"] += 1
        else:
            counts[mood] += 1
    
    return counts
