# Playlist Chaos - Logic Flow Diagram

## Overview

This diagram maps out the complete logic flow of the Playlist Chaos application, including both the Streamlit web interface ([`app.py`](app.py:1)) and the core playlist logic module ([`playlist_logic.py`](playlist_logic.py:1)).

```mermaid
flowchart TB
    subgraph APP["app.py - Streamlit Application"]
        MAIN["main()"]
        INIT["init_state()"]
        DEFAULT_SONGS["default_songs()"]
        PROFILE_SIDEBAR["profile_sidebar()"]
        ADD_SONG_SIDEBAR["add_song_sidebar()"]
        CLEAR_CONTROLS["clear_controls()"]
        PLAYLIST_TABS["playlist_tabs()"]
        RENDER_PLAYLIST["render_playlist()"]
        LUCKY_SECTION["lucky_section()"]
        STATS_SECTION["stats_section()"]
        HISTORY_SECTION["history_section()"]
    end

    subgraph LOGIC["playlist_logic.py - Core Logic Module"]
        NORMALIZE_TITLE["normalize_title()"]
        NORMALIZE_ARTIST["normalize_artist()"]
        NORMALIZE_GENRE["normalize_genre()"]
        NORMALIZE_SONG["normalize_song()"]
        CLASSIFY_SONG["classify_song()"]
        BUILD_PLAYLISTS["build_playlists()"]
        MERGE_PLAYLISTS["merge_playlists()"]
        COMPUTE_STATS["compute_playlist_stats()"]
        MOST_COMMON_ARTIST["most_common_artist()"]
        SEARCH_SONGS["search_songs()"]
        LUCKY_PICK["lucky_pick()"]
        RANDOM_CHOICE["random_choice_or_none()"]
        HISTORY_SUMMARY["history_summary()"]
    end

    subgraph DATA["Data Structures"]
        SONGS["songs: List[Song]"]
        PROFILE["profile: Dict"]
        HISTORY["history: List[Song]"]
        PLAYLISTS["playlists: PlaylistMap"]
        STATS["stats: Dict"]
    end

    MAIN --> INIT
    INIT --> SONGS
    INIT --> PROFILE
    INIT --> HISTORY

    MAIN --> PROFILE_SIDEBAR
    PROFILE_SIDEBAR --> PROFILE

    MAIN --> ADD_SONG_SIDEBAR
    ADD_SONG_SIDEBAR --> NORMALIZE_SONG
    NORMALIZE_SONG --> SONGS

    MAIN --> CLEAR_CONTROLS
    CLEAR_CONTROLS --> DEFAULT_SONGS
    DEFAULT_SONGS --> SONGS
    CLEAR_CONTROLS --> HISTORY

    MAIN --> BUILD_PLAYLISTS
    BUILD_PLAYLISTS --> SONGS
    BUILD_PLAYLISTS --> PROFILE
    BUILD_PLAYLISTS --> PLAYLISTS

    BUILD_PLAYLISTS --> NORMALIZE_SONG
    BUILD_PLAYLISTS --> CLASSIFY_SONG

    MAIN --> MERGE_PLAYLISTS
    MERGE_PLAYLISTS --> PLAYLISTS

    MAIN --> PLAYLIST_TABS
    PLAYLIST_TABS --> RENDER_PLAYLIST
    RENDER_PLAYLIST --> SEARCH_SONGS
    SEARCH_SONGS --> PLAYLISTS

    MAIN --> LUCKY_SECTION
    LUCKY_SECTION --> LUCKY_PICK
    LUCKY_PICK --> PLAYLISTS
    LUCKY_PICK --> RANDOM_CHOICE
    RANDOM_CHOICE --> HISTORY

    MAIN --> STATS_SECTION
    STATS_SECTION --> COMPUTE_STATS
    COMPUTE_STATS --> PLAYLISTS
    COMPUTE_STATS --> MOST_COMMON_ARTIST
    COMPUTE_STATS --> STATS

    MAIN --> HISTORY_SECTION
    HISTORY_SECTION --> HISTORY
    HISTORY_SECTION --> HISTORY_SUMMARY

    NORMALIZE_SONG --> NORMALIZE_TITLE
    NORMALIZE_SONG --> NORMALIZE_ARTIST
    NORMALIZE_SONG --> NORMALIZE_GENRE

    CLASSIFY_SONG --> SONG
    CLASSIFY_SONG --> PROFILE

    classDef app fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef logic fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#4a148c,stroke-width:2px

    class MAIN,INIT,DEFAULT_SONGS,PROFILE_SIDEBAR,ADD_SONG_SIDEBAR,CLEAR_CONTROLS,PLAYLIST_TABS,RENDER_PLAYLIST,LUCKY_SECTION,STATS_SECTION,HISTORY_SECTION app
    class NORMALIZE_TITLE,NORMALIZE_ARTIST,NORMALIZE_GENRE,NORMALIZE_SONG,CLASSIFY_SONG,BUILD_PLAYLISTS,MERGE_PLAYLISTS,COMPUTE_STATS,MOST_COMMON_ARTIST,SEARCH_SONGS,LUCKY_PICK,RANDOM_CHOICE,HISTORY_SUMMARY logic
    class SONGS,PROFILE,HISTORY,PLAYLISTS,STATS data
```

## Detailed Logic Flow

### 1. Application Initialization

```mermaid
flowchart TB
    START([Script Start])
    CHECK_MAIN{Is __name__ == '__main__'?}
    YES_MAIN[Yes - Call main]
    NO_MAIN[No - Skip main]
    END([End])
    
    MAIN_FUNC[main function]
    PAGE_CONFIG[st.set_page_config]
    TITLE[st.title]
    DESC[st.write description]
    INIT_STATE[init_state]
    
    CHECK_SONGS{songs in session state?}
    YES_SONGS[Yes - Use existing]
    NO_SONGS[No - Load defaults]
    LOAD_DEFAULT[Load default songs]
    
    CHECK_PROFILE{profile in session state?}
    YES_PROFILE[Yes - Use existing]
    NO_PROFILE[No - Load defaults]
    LOAD_PROFILE[Load default profile]
    
    CHECK_HISTORY{history in session state?}
    YES_HISTORY[Yes - Use existing]
    NO_HISTORY[No - Initialize]
    INIT_HISTORY[Init empty history]
    
    RENDER_SIDEBAR[Render sidebar controls]
    BUILD[Build playlists]
    
    START --> CHECK_MAIN
    CHECK_MAIN --> YES_MAIN
    CHECK_MAIN --> NO_MAIN
    YES_MAIN --> MAIN_FUNC
    NO_MAIN --> END
    MAIN_FUNC --> PAGE_CONFIG
    PAGE_CONFIG --> TITLE
    TITLE --> DESC
    DESC --> INIT_STATE
    INIT_STATE --> CHECK_SONGS
    
    CHECK_SONGS --> YES_SONGS
    CHECK_SONGS --> NO_SONGS
    NO_SONGS --> LOAD_DEFAULT
    LOAD_DEFAULT --> CHECK_PROFILE
    YES_SONGS --> CHECK_PROFILE
    
    CHECK_PROFILE --> YES_PROFILE
    CHECK_PROFILE --> NO_PROFILE
    NO_PROFILE --> LOAD_PROFILE
    LOAD_PROFILE --> CHECK_HISTORY
    YES_PROFILE --> CHECK_HISTORY
    
    CHECK_HISTORY --> YES_HISTORY
    CHECK_HISTORY --> NO_HISTORY
    NO_HISTORY --> INIT_HISTORY
    INIT_HISTORY --> RENDER_SIDEBAR
    YES_HISTORY --> RENDER_SIDEBAR
    
    RENDER_SIDEBAR --> BUILD
```

### 2. Song Classification Logic

```mermaid
flowchart TB
    CLASSIFY["classify_song"] --> EXTRACT
    EXTRACT[Extract song attributes] --> ENERGY
    ENERGY[energy = song.get] --> GENRE
    GENRE[genre = song.get] --> TITLE
    TITLE[title = song.get] --> EXTRACT_PROFILE

    EXTRACT_PROFILE[Extract profile] --> HYPE_MIN
    HYPE_MIN[hype_min_energy] --> CHILL_MAX
    CHILL_MAX[chill_max_energy] --> FAV_GENRE
    FAV_GENRE[favorite_genre] --> CHECK_HYPE

    CHECK_HYPE{Check Hype Criteria} --> GENRE_MATCH
    GENRE_MATCH{genre matches favorite?} --> YES_GENRE
    YES_GENRE[Yes] --> RETURN_HYPE
    CHECK_HYPE --> ENERGY_HIGH
    ENERGY_HIGH{energy >= hype threshold?} --> YES_ENERGY
    YES_ENERGY[Yes] --> RETURN_HYPE
    CHECK_HYPE --> HYPE_KEYWORD
    HYPE_KEYWORD{hype keyword in genre?} --> YES_HYPE_KW
    YES_HYPE_KW[Yes] --> RETURN_HYPE

    GENRE_MATCH --> NO_GENRE
    NO_GENRE[No] --> CHECK_CHILL
    ENERGY_HIGH --> NO_ENERGY
    NO_ENERGY[No] --> CHECK_CHILL
    HYPE_KEYWORD --> NO_HYPE_KW
    NO_HYPE_KW[No] --> CHECK_CHILL

    CHECK_CHILL{Check Chill Criteria} --> ENERGY_LOW
    ENERGY_LOW{energy <= chill threshold?} --> YES_LOW
    YES_LOW[Yes] --> RETURN_CHILL
    CHECK_CHILL --> CHILL_KEYWORD
    CHILL_KEYWORD{chill keyword in title?} --> YES_CHILL_KW
    YES_CHILL_KW[Yes] --> RETURN_CHILL

    ENERGY_LOW --> NO_LOW
    NO_LOW[No] --> RETURN_MIXED
    CHILL_KEYWORD --> NO_CHILL_KW
    NO_CHILL_KW[No] --> RETURN_MIXED

    RETURN_HYPE[Return Hype]
    RETURN_CHILL[Return Chill]
    RETURN_MIXED[Return Mixed]
```

### 3. Playlist Building Process

```mermaid
flowchart TB
    BUILD["build_playlists"] --> INIT_PLAYLISTS
    INIT_PLAYLISTS[Initialize playlists] --> HYPE_LIST
    HYPE_LIST["Hype: []"] --> CHILL_LIST
    CHILL_LIST["Chill: []"] --> MIXED_LIST
    MIXED_LIST["Mixed: []"] --> LOOP

    LOOP{For each song} --> NORMALIZE
    NORMALIZE[normalize_song] --> NORM_TITLE
    NORM_TITLE[normalize_title] --> NORM_ARTIST
    NORM_ARTIST[normalize_artist] --> NORM_GENRE
    NORM_GENRE[normalize_genre] --> PARSE_ENERGY
    PARSE_ENERGY[Parse energy] --> PARSE_TAGS
    PARSE_TAGS[Parse tags] --> CLASSIFY

    CLASSIFY[classify_song] --> GET_MOOD
    GET_MOOD[Get mood] --> ADD_MOOD
    ADD_MOOD[Add mood to song] --> APPEND
    APPEND[Append to playlist] --> LOOP

    LOOP --> DONE
    DONE[Done] --> RETURN
    RETURN[Return playlists]
```

### 4. Lucky Pick Feature

```mermaid
flowchart TB
    LUCKY["lucky_pick"] --> CHECK_MODE
    CHECK_MODE{Select mode} --> MODE_HYPE
    MODE_HYPE[hype] --> GET_HYPE
    GET_HYPE[Get Hype playlist] --> RANDOM
    CHECK_MODE --> MODE_CHILL
    MODE_CHILL[chill] --> GET_CHILL
    GET_CHILL[Get Chill playlist] --> RANDOM
    CHECK_MODE --> MODE_ANY
    MODE_ANY[any] --> COMBINE
    COMBINE[Combine playlists] --> RANDOM

    RANDOM[random_choice] --> CHECK_EMPTY
    CHECK_EMPTY{Songs empty?} --> YES_EMPTY
    YES_EMPTY[Yes] --> RETURN_NONE
    RETURN_NONE[Return None]
    CHECK_EMPTY --> NO_EMPTY
    NO_EMPTY[No] --> CHOICE
    CHOICE[Random choice] --> RETURN_SONG
    RETURN_SONG[Return song]
```

### 5. Statistics Computation

```mermaid
flowchart TB
    COMPUTE["compute_playlist_stats"] --> COLLECT
    COLLECT[Collect all songs] --> EXTEND
    EXTEND[Extend all_songs] --> EXTRACT_PLAYLISTS

    EXTRACT_PLAYLISTS[Extract playlists] --> HYPE
    HYPE[hype = get] --> CHILL
    CHILL[chill = get] --> MIXED
    MIXED[mixed = get] --> CALC_RATIO

    CALC_RATIO[Calculate ratio] --> RATIO
    RATIO[Divide hype by hype] --> CALC_AVG

    CALC_AVG[Calculate avg_energy] --> SUM_ENERGY
    SUM_ENERGY[Sum Hype energy] --> DIVIDE
    DIVIDE[Divide by total] --> FIND_TOP

    FIND_TOP[most_common_artist] --> COUNT_ARTISTS
    COUNT_ARTISTS[Count artists] --> SORT
    SORT[Sort by count] --> RETURN_TOP
    RETURN_TOP[Return top artist] --> RETURN_STATS

    RETURN_STATS[Return stats] --> TOTAL
    TOTAL["total_songs"] --> HYPE_COUNT
    HYPE_COUNT["hype_count"] --> CHILL_COUNT
    CHILL_COUNT["chill_count"] --> MIXED_COUNT
    MIXED_COUNT["mixed_count"] --> HYPE_RATIO
    HYPE_RATIO["hype_ratio"] --> AVG_ENERGY
    AVG_ENERGY["avg_energy"] --> TOP_ARTIST
    TOP_ARTIST["top_artist"] --> TOP_COUNT
    TOP_COUNT["top_artist_count"]
```

### 6. Search Functionality

```mermaid
flowchart TB
    SEARCH["search_songs"] --> CHECK_QUERY
    CHECK_QUERY{Query empty?} --> YES_QUERY
    YES_QUERY[Yes] --> RETURN_ALL
    RETURN_ALL[Return all songs]
    CHECK_QUERY --> NO_QUERY
    NO_QUERY[No] --> NORMALIZE

    NORMALIZE[Normalize query] --> LOOP
    LOOP{For each song} --> GET_VALUE
    GET_VALUE[value = get] --> TO_LOWER
    TO_LOWER[value.lower] --> CHECK_CONTAIN
    CHECK_CONTAIN{value in q?} --> YES_CONTAIN
    YES_CONTAIN[Yes] --> APPEND
    APPEND[Append to filtered] --> LOOP
    CHECK_CONTAIN --> NO_CONTAIN
    NO_CONTAIN[No] --> LOOP

    LOOP --> DONE
    DONE[Done] --> RETURN_FILTERED
    RETURN_FILTERED[Return filtered]
```

### 7. History Summary

```mermaid
flowchart TB
    SUMMARY["history_summary"] --> INIT_COUNTS
    INIT_COUNTS[Initialize counts] --> HYPE_COUNT
    HYPE_COUNT["Hype: 0"] --> CHILL_COUNT
    CHILL_COUNT["Chill: 0"] --> MIXED_COUNT
    MIXED_COUNT["Mixed: 0"] --> LOOP

    LOOP{For each song} --> GET_MOOD
    GET_MOOD[mood = get] --> CHECK_VALID
    CHECK_VALID{mood in counts?} --> YES_VALID
    YES_VALID[Yes] --> INCREMENT
    INCREMENT[Increment mood] --> LOOP
    CHECK_VALID --> NO_VALID
    NO_VALID[No] --> INCREMENT_MIXED
    INCREMENT_MIXED[Increment Mixed] --> LOOP

    LOOP --> DONE
    DONE[Done] --> RETURN
    RETURN[Return counts]
```

## Data Flow Summary

### Song Data Structure
```mermaid
classDiagram
    class Song {
        +str title
        +str artist
        +str genre
        +int energy
        +list tags
        +str mood
    }
    class PlaylistMap {
        +list Hype
        +list Chill
        +list Mixed
    }
    class Profile {
        +str name
        +int hype_min_energy
        +int chill_max_energy
        +str favorite_genre
        +bool include_mixed
    }
    class Stats {
        +int total_songs
        +int hype_count
        +int chill_count
        +int mixed_count
        +float hype_ratio
        +float avg_energy
        +str top_artist
        +int top_artist_count
    }

    PlaylistMap "*" --> "*" Song
    Profile --> Song : classifies
    Stats --> PlaylistMap : computes from
```

## Key Relationships

1. **Normalization Pipeline**: [`normalize_song()`](playlist_logic.py:123) → [`normalize_title()`](playlist_logic.py:36), [`normalize_artist()`](playlist_logic.py:65), [`normalize_genre()`](playlist_logic.py:97)
2. **Classification**: [`classify_song()`](playlist_logic.py:176) uses profile to determine mood
3. **Playlist Building**: [`build_playlists()`](playlist_logic.py:257) normalizes and classifies each song
4. **UI Integration**: [`app.py`](app.py:1) functions call [`playlist_logic.py`](playlist_logic.py:1) functions
5. **State Management**: Streamlit session state holds songs, profile, and history
