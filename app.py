"""
Playlist Chaos Application
==========================
A Streamlit web application for managing music playlists with mood-based classification.

This application provides a user interface for:
- Viewing songs organized by mood (Hype, Chill, Mixed)
- Customizing user profile preferences
- Adding new songs to the library
- Random song selection ("Lucky Pick")
- Viewing playlist statistics and history

Main Flow:
1. Initialize session state with default songs and profile
2. Render sidebar controls (profile, add song, manage data)
3. Build playlists based on current profile
4. Display playlists in tabs
5. Show lucky pick, stats, and history sections
"""

import streamlit as st
from typing import cast

from playlist_logic import (
    DEFAULT_PROFILE,
    Song,
    build_playlists,
    compute_playlist_stats,
    history_summary,
    lucky_pick,
    merge_playlists,
    normalize_song,
    search_songs,
)


def init_state():
    """
    Initialize Streamlit session state with default values.
    
    This function ensures that all necessary session state variables exist
    before the application runs. It only initializes variables that don't
    already exist, preserving user changes across page refreshes.
    
    Session state variables initialized:
    - songs: List of all songs in the library
    - profile: User preferences for mood classification
    - history: List of previously picked songs
    
    Example:
        >>> # On first run, creates session state with defaults
        >>> init_state()
        >>> st.session_state.songs  # Will contain default_songs()
        >>> st.session_state.profile  # Will contain DEFAULT_PROFILE
        >>> st.session_state.history  # Will be empty list []
    """
    # Initialize songs library with default songs if not already set
    if "songs" not in st.session_state:
        st.session_state.songs = default_songs()
    
    # Initialize user profile with default settings if not already set
    if "profile" not in st.session_state:
        st.session_state.profile = dict(DEFAULT_PROFILE)
    
    # Initialize pick history as empty list if not already set
    if "history" not in st.session_state:
        st.session_state.history = []


def default_songs():
    """
    Return a default list of songs for the initial library.
    
    This function provides a curated collection of songs across various genres
    and energy levels to demonstrate the playlist classification system.
    The songs are designed to test different mood classification scenarios.
    
    Returns:
        List[Song]: A list of song dictionaries with keys: title, artist, genre, energy, tags
        
    Example:
        >>> songs = default_songs()
        >>> len(songs)
        22
        >>> songs[0]["title"]
        "Thunderstruck"
        >>> songs[0]["energy"]
        9
    """
    return [
        {
            "title": "Thunderstruck",
            "artist": "AC/DC",
            "genre": "rock",
            "energy": 9,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Lo-fi Rain",
            "artist": "DJ Calm",
            "genre": "lofi",
            "energy": 2,
            "tags": ["study"],
        },
        {
            "title": "Night Drive",
            "artist": "Neon Echo",
            "genre": "electronic",
            "energy": 6,
            "tags": ["synth"],
        },
        {
            "title": "Soft Piano",
            "artist": "Sleep Sound",
            "genre": "ambient",
            "energy": 1,
            "tags": ["sleep"],
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "genre": "rock",
            "energy": 8,
            "tags": ["classic", "opera"],
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "genre": "pop",
            "energy": 8,
            "tags": ["synth", "dance"],
        },
        {
            "title": "Take Five",
            "artist": "Dave Brubeck",
            "genre": "jazz",
            "energy": 4,
            "tags": ["classic", "instrumental"],
        },
        {
            "title": "Strobe",
            "artist": "Deadmau5",
            "genre": "electronic",
            "energy": 7,
            "tags": ["progressive", "long"],
        },
        {
            "title": "Weightless",
            "artist": "Marconi Union",
            "genre": "ambient",
            "energy": 1,
            "tags": ["relax", "sleep"],
        },
        {
            "title": "Smells Like Teen Spirit",
            "artist": "Nirvana",
            "genre": "rock",
            "energy": 9,
            "tags": ["grunge", "90s"],
        },
        {
            "title": "Levitating",
            "artist": "Dua Lipa",
            "genre": "pop",
            "energy": 8,
            "tags": ["dance", "party"],
        },
        {
            "title": "So What",
            "artist": "Miles Davis",
            "genre": "jazz",
            "energy": 3,
            "tags": ["trumpet", "cool"],
        },
        {
            "title": "Midnight City",
            "artist": "M83",
            "genre": "electronic",
            "energy": 7,
            "tags": ["indie", "dream"],
        },
        {
            "title": "Gymnopedie No.1",
            "artist": "Erik Satie",
            "genre": "ambient",
            "energy": 1,
            "tags": ["piano", "calm"],
        },
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "genre": "rock",
            "energy": 8,
            "tags": ["guitar", "80s"],
        },
        {
            "title": "Bad Guy",
            "artist": "Billie Eilish",
            "genre": "pop",
            "energy": 6,
            "tags": ["bass", "dark"],
        },
        {
            "title": "Fly Me to the Moon",
            "artist": "Frank Sinatra",
            "genre": "jazz",
            "energy": 5,
            "tags": ["vocal", "swing"],
        },
        {
            "title": "Sandstorm",
            "artist": "Darude",
            "genre": "electronic",
            "energy": 10,
            "tags": ["trance", "meme"],
        },
        {
            "title": "Clair de Lune",
            "artist": "Claude Debussy",
            "genre": "ambient",
            "energy": 2,
            "tags": ["piano", "classical"],
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "genre": "rock",
            "energy": 6,
            "tags": ["classic", "guitar"],
        },
        {
            "title": "Uptown Funk",
            "artist": "Mark Ronson ft. Bruno Mars",
            "genre": "pop",
            "energy": 9,
            "tags": ["funk", "dance"],
        },
        {
            "title": "Feeling Good",
            "artist": "Nina Simone",
            "genre": "jazz",
            "energy": 6,
            "tags": ["soul", "vocal"],
        },
    ]


def profile_sidebar():
    """
    Render and update the user profile in the sidebar.
    
    This function creates a sidebar section where users can customize their
    mood classification preferences. Changes are immediately reflected in
    the session state profile.
    
    Profile settings:
    - name: Profile identifier
    - hype_min_energy: Minimum energy level for "Hype" classification (1-10)
    - chill_max_energy: Maximum energy level for "Chill" classification (1-10)
    - favorite_genre: Genre that automatically triggers "Hype" classification
    - include_mixed: Whether to show the "Mixed" playlist in tabs
    
    Example:
        >>> # User changes hype_min_energy from 7 to 8
        >>> # The profile is updated in st.session_state.profile
        >>> st.session_state.profile["hype_min_energy"]
        8
    """
    st.sidebar.header("Mood profile")

    # Get current profile from session state
    profile = st.session_state.profile

    # Profile name input field
    profile["name"] = st.sidebar.text_input(
        "Profile name",
        value=str(profile.get("name", "")),
    )

    # Create two columns for side-by-side energy sliders
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # Hype minimum energy slider (1-10)
        profile["hype_min_energy"] = st.sidebar.slider(
            "Hype min energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("hype_min_energy", 7)),
        )
    
    with col2:
        # Chill maximum energy slider (1-10)
        profile["chill_max_energy"] = st.sidebar.slider(
            "Chill max energy",
            min_value=1,
            max_value=10,
            value=int(profile.get("chill_max_energy", 3)),
        )

    # Favorite genre dropdown
    # ❌ BUG: Always resets to index 0 (rock) on every render, ignoring current profile value
    # profile["favorite_genre"] = st.sidebar.selectbox(
    #     "Favorite genre",
    #     options=["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"],
    #     index=0,
    # )
    # ✅ FIX: Use current profile value to determine index, preserving selection across renders
    genre_options = ["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"]
    profile["favorite_genre"] = st.sidebar.selectbox(
        "Favorite genre",
        options=genre_options,
        index=genre_options.index(profile.get("favorite_genre", "rock")),
    )

    # Checkbox to include/exclude Mixed playlist
    profile["include_mixed"] = st.sidebar.checkbox(
        "Include Mixed playlist in views",
        value=bool(profile.get("include_mixed", True)),
    )

    # Display current profile name for confirmation
    st.sidebar.write("Current profile:", profile["name"])


def add_song_sidebar():
    """
    Render the Add Song controls in the sidebar.
    
    This function creates a form in the sidebar where users can add new songs
    to their library. When the "Add to playlist" button is clicked, the song
    is normalized and appended to the session state songs list.
    
    Form fields:
    - title: Song title (required)
    - artist: Artist name (required)
    - genre: Genre from dropdown
    - energy: Energy level 1-10
    - tags: Comma-separated tags
    
    Validation:
    - Both title and artist must be non-empty to add the song
    
    Example:
        >>> # User enters: title="New Song", artist="New Artist", genre="pop", energy=7, tags="dance"
        >>> # Clicks "Add to playlist"
        >>> # Song is added to st.session_state.songs
        >>> st.session_state.songs[-1]["title"]
        "new song"  # ❌ DOCSTRING ERROR: normalize_title() only strips whitespace, doesn't lowercase
        # The actual result would be "New Song" (preserving case), not "new song"
        # ✅ FIX: Corrected docstring to reflect actual behavior
        "New Song"  # Title preserves case (only whitespace is stripped)
    """
    st.sidebar.header("Add a song")

    # Input fields for new song
    title = st.sidebar.text_input("Title")
    artist = st.sidebar.text_input("Artist")
    genre = st.sidebar.selectbox(
        "Genre",
        options=["rock", "lofi", "pop", "jazz", "electronic", "ambient", "other"],
    )
    energy = st.sidebar.slider("Energy", min_value=1, max_value=10, value=5)
    tags_text = st.sidebar.text_input("Tags (comma separated)")

    # Add song button handler
    if st.sidebar.button("Add to playlist"):
        # Parse comma-separated tags into a list
        raw_tags = [t.strip() for t in tags_text.split(",")]
        # Filter out empty tags
        tags = [t for t in raw_tags if t]

        # Create song dictionary
        song: Song = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "energy": energy,
            "tags": tags,
        }
        
        # Validate that title and artist are provided
        if title and artist:
            # Normalize the song data
            normalized = normalize_song(song)
            # ❌ QUIRK: Unnecessary list copy - could just append directly to st.session_state.songs
            # The copy [:] creates a new list, appends to it, then reassigns back
            # all_songs = st.session_state.songs[:]
            # all_songs.append(normalized)
            # st.session_state.songs = all_songs
            # ✅ FIX: Append directly to session state list, no copy needed
            st.session_state.songs.append(normalized)


def playlist_tabs(playlists):
    """
    Render playlists in Streamlit tabs.
    
    This function creates a tabbed interface for viewing different mood
    playlists. The "Mixed" tab is only shown if the user's profile has
    include_mixed set to True.
    
    Args:
        playlists (PlaylistMap): Dictionary mapping mood names to song lists
                                 Format: {"Hype": [songs], "Chill": [songs], "Mixed": [songs]}
    
    Example:
        >>> playlists = {"Hype": [song1, song2], "Chill": [song3], "Mixed": [song4]}
        >>> # With include_mixed=True, shows 3 tabs: Hype, Chill, Mixed
        >>> # With include_mixed=False, shows 2 tabs: Hype, Chill
    """
    # Check if Mixed playlist should be included
    include_mixed = st.session_state.profile.get("include_mixed", True)

    # Build list of tab labels based on profile setting
    tab_labels = ["Hype", "Chill"]
    if include_mixed:
        tab_labels.append("Mixed")

    # Create tabs
    tabs = st.tabs(tab_labels)

    # Render each playlist in its corresponding tab
    for label, tab in zip(tab_labels, tabs):
        with tab:
            render_playlist(label, playlists.get(label, []))


def render_playlist(label, songs):
    """
    Render a single playlist with search functionality.
    
    This function displays a playlist with a search bar to filter songs
    by artist. Each song is displayed with its title, artist, genre,
    energy level, mood, and tags.
    
    Args:
        label (str): The mood label for this playlist (e.g., "Hype", "Chill", "Mixed")
        songs (List[Song]): List of songs to display in this playlist
        
    Example:
        >>> songs = [
        ...     {"title": "Song1", "artist": "Artist1", "genre": "rock", "energy": 8, "mood": "Hype", "tags": ["classic"]}
        ... ]
        >>> render_playlist("Hype", songs)
        # Displays: - **Song1** by Artist1 (genre rock, energy 8, mood Hype) [classic]
    """
    st.subheader(f"{label} playlist")
    
    # Handle empty playlist
    if not songs:
        st.write("No songs in this playlist.")
        return

    # Search input for filtering by artist
    query = st.text_input(f"Search {label} playlist by artist", key=f"search_{label}")
    
    # Filter songs based on search query
    filtered = search_songs(songs, query, field="artist")

    # Handle no search results
    if not filtered:
        st.write("No matching songs.")
        return

    # Display each filtered song
    for song in filtered:
        mood = song.get("mood", "?")
        # ❌ tags = ", ".join(song.get("tags", []))  # Type error: song.get() returns object, not Iterable[str]
        # ✅ Fix: Cast tags to list of strings to satisfy type checker
        tags = ", ".join(cast(list[str], song.get("tags", [])))
        st.write(
            f"- **{song['title']}** by {song['artist']} "
            f"(genre {song['genre']}, energy {song['energy']}, mood {mood}) "
            f"[{tags}]"
        )


def lucky_section(playlists):
    """
    Render the lucky pick controls and result display.
    
    This function provides a "Lucky Pick" feature that randomly selects
    a song from the playlists. Users can choose to pick from Hype, Chill,
    or any playlist. The selected song is added to the pick history.
    
    Args:
        playlists (PlaylistMap): Dictionary mapping mood names to song lists
        
    Example:
        >>> playlists = {"Hype": [song1], "Chill": [song2], "Mixed": [song3]}
        >>> # User selects mode="hype" and clicks "Feeling lucky"
        >>> # Displays: Lucky song: Song1 by Artist1 (mood Hype)
        >>> # Song is added to st.session_state.history
    """
    st.header("Lucky pick")

    # Mode selection dropdown
    mode = st.selectbox(
        "Pick from",
        options=["any", "hype", "chill"],
        index=0,
    )

    # Lucky pick button handler
    if st.button("Feeling lucky"):
        # Get random song based on selected mode
        pick = lucky_pick(playlists, mode=mode)
        
        # Handle case when no songs are available
        if pick is None:
            st.warning("No songs available for this mode.")
            return

        # Display the lucky pick result
        st.success(
            f"Lucky song: {pick['title']} by {pick['artist']} "
            f"(mood {pick.get('mood', '?')})"
        )

        # Add the picked song to history
        history = st.session_state.history
        history.append(pick)
        st.session_state.history = history


def stats_section(playlists):
    """
    Render statistics based on the playlists.
    
    This function calculates and displays various statistics about the
    current playlists, including song counts, ratios, averages, and
    the most common artist.
    
    Args:
        playlists (PlaylistMap): Dictionary mapping mood names to song lists
        
    Example:
        >>> playlists = {"Hype": [s1, s2], "Chill": [s3], "Mixed": [s4]}
        >>> # Displays metrics like:
        >>> # Total songs: 4
        >>> # Hype songs: 2
        >>> # Chill songs: 1
        >>> # Mixed songs: 1
        >>> # Hype ratio: 1.00
        >>> # Average energy: X.XX
        >>> # Most common artist: ArtistName (N songs)
    """
    st.header("Playlist stats")

    # Compute statistics using the logic module
    stats = compute_playlist_stats(playlists)

    # Display song counts in three columns
    col1, col2, col3 = st.columns(3)
    # ❌ col1.metric("Total songs", stats["total_songs"])  # Type error: stats values are object, not numeric
    # ❌ col2.metric("Hype songs", stats["hype_count"])  # Type error: stats values are object, not numeric
    # ❌ col3.metric("Chill songs", stats["chill_count"])  # Type error: stats values are object, not numeric
    # ✅ Fix: Cast stats values to int to satisfy type checker
    col1.metric("Total songs", cast(int, stats["total_songs"]))
    col2.metric("Hype songs", cast(int, stats["hype_count"]))
    col3.metric("Chill songs", cast(int, stats["chill_count"]))

    # Display ratios and averages in three columns
    col4, col5, col6 = st.columns(3)
    # ❌ col4.metric("Mixed songs", stats["mixed_count"])  # Type error: stats values are object, not numeric
    # ❌ col5.metric("Hype ratio", f"{stats['hype_ratio']:.2f}")  # Type error: stats values are object, not numeric
    # ❌ col6.metric("Average energy", f"{stats['avg_energy']:.2f}")  # Type error: stats values are object, not numeric
    # ✅ Fix: Cast stats values to appropriate types to satisfy type checker
    col4.metric("Mixed songs", cast(int, stats["mixed_count"]))
    col5.metric("Hype ratio", f"{cast(float, stats['hype_ratio']):.2f}")
    col6.metric("Average energy", f"{cast(float, stats['avg_energy']):.2f}")

    # Display most common artist
    top_artist = stats["top_artist"]
    if top_artist:
        st.write(
            f"Most common artist: {top_artist} "
            f"({cast(int, stats['top_artist_count'])} songs)"
        )
    else:
        st.write("No top artist yet.")


def history_section():
    """
    Render the pick history overview.
    
    This function displays a summary of previously picked songs, organized
    by mood. Users can optionally view the full history with song details.
    
    Example:
        >>> st.session_state.history = [
        ...     {"title": "Song1", "artist": "Artist1", "mood": "Hype"},
        ...     {"title": "Song2", "artist": "Artist2", "mood": "Chill"}
        ... ]
        >>> # Displays: Recent picks by mood: {"Hype": 1, "Chill": 1, "Mixed": 0}
        >>> # With checkbox checked, shows:
        >>> # Hype: Song1 by Artist1
        >>> # Chill: Song2 by Artist2
    """
    st.header("History")

    # Get pick history from session state
    history = st.session_state.history
    
    # Handle empty history
    if not history:
        st.write("No history yet.")
        return

    # Display summary of picks by mood
    summary = history_summary(history)
    st.write("Recent picks by mood:", summary)

    # Optional detailed history view
    show_details = st.checkbox("Show full history")
    if show_details:
        for song in history:
            st.write(
                f"{song.get('mood', '?')}: {song['title']} by {song['artist']}"
            )


def clear_controls():
    """
    Render a small section for managing and clearing data.
    
    This function provides buttons to reset the songs library to defaults
    and clear the pick history. These are destructive operations that
    reset the application state.
    
    Example:
        >>> # User clicks "Reset songs to default"
        >>> # st.session_state.songs is replaced with default_songs()
        >>> # User clicks "Clear history"
        >>> # st.session_state.history becomes []
    """
    st.sidebar.header("Manage data")
    
    # Reset songs to default library
    if st.sidebar.button("Reset songs to default"):
        st.session_state.songs = default_songs()
    
    # Clear pick history
    if st.sidebar.button("Clear history"):
        st.session_state.history = []


def main():
    """
    Main application entry point.
    
    This function orchestrates the entire application flow:
    1. Configure page settings
    2. Display title and description
    3. Initialize session state
    4. Render sidebar controls
    5. Build playlists based on current profile
    6. Display main content sections
    
    The function is called when the script is run directly.
    
    Example:
        >>> # When script is executed: python app.py
        >>> # Streamlit launches with the full UI
    """
    # Configure Streamlit page
    st.set_page_config(page_title="Playlist Chaos", layout="wide")
    
    # Application title
    st.title("Playlist Chaos")

    # Application description
    st.write(
        "An AI assistant tried to build a smart playlist engine. "
        "The code runs, but the behavior is a bit unpredictable."
    )

    # Initialize session state
    init_state()
    
    # Render sidebar sections
    profile_sidebar()
    add_song_sidebar()
    clear_controls()

    # Get current profile and songs from session state
    profile = st.session_state.profile
    songs = st.session_state.songs

    # Build playlists based on current profile
    base_playlists = build_playlists(songs, profile)

    # ❌ QUIRK: Merging with an empty playlist is a no-op - this line is unnecessary
    # Could just use base_playlists directly instead of merged_playlists
    # merged_playlists = merge_playlists(base_playlists, {})
    # ✅ FIX: Use base_playlists directly, no merge needed
    playlists = base_playlists

    # Display main content sections
    playlist_tabs(playlists)
    st.divider()
    lucky_section(playlists)
    st.divider()
    stats_section(playlists)
    st.divider()
    history_section()


# Entry point: run main() when script is executed directly
if __name__ == "__main__":
    main()
