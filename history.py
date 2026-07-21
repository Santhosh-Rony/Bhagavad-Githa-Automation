import os
import json
from typing import List, Dict
from logger import logger

HISTORY_FILE = "posted_characters.json"
STATE_FILE = "posting_state.json"

def load_history() -> List[str]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load history: {e}")
        return []

def save_history(character_name: str):
    history = load_history()
    if character_name not in history:
        history.append(character_name)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_posting_state() -> dict:
    default_state = {"current_character": None, "date": None, "generic_music_index": 0}
    if not os.path.exists(STATE_FILE):
        return default_state
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            if not isinstance(state, dict):
                return default_state
            if "current_character" not in state:
                state["current_character"] = None
            if "date" not in state:
                state["date"] = None
            if "generic_music_index" not in state:
                state["generic_music_index"] = 0
            return state
    except Exception as e:
        logger.warning(f"Failed to load posting state: {e}")
        return default_state

def update_posting_state(character: str, current_date: str = None, generic_music_index: int = None):
    state = get_posting_state()
    state["current_character"] = character
        
    if current_date:
        state["date"] = current_date
        
    if generic_music_index is not None:
        state["generic_music_index"] = generic_music_index
        
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def clear_posting_state():
    state = get_posting_state()
    state["current_character"] = None
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
