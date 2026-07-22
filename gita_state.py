import os
import json
from logger import logger
from gita_chapters import GITA_CHAPTERS, TOTAL_CHAPTERS

STATE_FILE = "gita_state.json"

# Music rotates across all 12 tracks
MUSIC_POOL = ["music/music.mp3"] + [f"music/music{i}.mp3" for i in range(1, 12)]

def load_state() -> dict:
    """Load current chapter, verse and music index from state file."""
    if not os.path.exists(STATE_FILE):
        return {"chapter": 1, "verse": 1, "music_index": 0}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
            # Ensure all keys exist with defaults
            state.setdefault("chapter", 1)
            state.setdefault("verse", 1)
            state.setdefault("music_index", 0)
            return state
    except Exception as e:
        logger.warning(f"Could not read gita_state.json, starting fresh. Error: {e}")
        return {"chapter": 1, "verse": 1, "music_index": 0}

def save_state(state: dict):
    """Persist the current state to disk."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
        logger.info(f"State saved: Chapter {state['chapter']}, Verse {state['verse']}, Music index {state['music_index']}")
    except Exception as e:
        logger.error(f"Failed to save gita_state.json: {e}")

def get_current_verse() -> tuple[int, int]:
    """Returns (chapter, verse) for the current post."""
    state = load_state()
    return state["chapter"], state["verse"]

def get_current_music() -> str:
    """Returns the current music file path."""
    state = load_state()
    idx = state.get("music_index", 0) % len(MUSIC_POOL)
    return MUSIC_POOL[idx]

def advance_state():
    """
    Increments to the next verse after a successful post.
    Moves to next chapter when current chapter is exhausted.
    Wraps back to Chapter 1 Verse 1 after all 700 verses are complete.
    """
    state = load_state()
    chapter = state["chapter"]
    verse = state["verse"]
    music_index = state.get("music_index", 0)

    max_verses = GITA_CHAPTERS.get(chapter, 1)

    if verse < max_verses:
        # Next verse in the same chapter
        verse += 1
    else:
        # Move to next chapter
        chapter += 1
        verse = 1
        if chapter > TOTAL_CHAPTERS:
            # All 700 verses complete — loop back to the beginning
            logger.info("🎉 All 700 Bhagavad Gita verses completed! Restarting from Chapter 1, Verse 1.")
            chapter = 1
            verse = 1

    # Advance music index (loops within MUSIC_POOL)
    music_index = (music_index + 1) % len(MUSIC_POOL)

    new_state = {"chapter": chapter, "verse": verse, "music_index": music_index}
    save_state(new_state)
    logger.info(f"Advanced to: Chapter {chapter}, Verse {verse}")
