# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PhantomThrill is a visual novel / life-sim RPG about a fresh graduate who becomes a phantom thief. Available as both a browser game and text-based Python game, sharing the same game data.

## Running the Games

**Browser version:**
```bash
open index.html
```

**Text-based Python version:**
```bash
python3 game.py
```

## Build System

After editing `game_data.json`, run the build script to update the HTML version:
```bash
python3 build.py
```

This embeds the JSON data into `index.html` as a JavaScript constant (`GAME_DATA`), converting snake_case keys to camelCase.

## Architecture

### Shared Data Model
- `game_data.json` - Single source of truth for all game content
  - `meta` - Title, credits
  - `initial_state` - Starting stats, flags, inventory
  - `locations` - All visitable locations with actions
  - `actions` - Action definitions with costs, effects, messages
  - `dialogues` - All story dialogue sequences
  - `heist_sequences` - Heist phase definitions with stat requirements
  - `endings` - Game ending texts
  - `objectives` - Objective text for story progress

### Dual Implementation
- `index.html` - Browser game (HTML + CSS + JavaScript)
- `game.py` - Terminal game (Python)

Both read from `game_data.json`. The HTML version uses embedded `GAME_DATA` (built by `build.py`), the Python version loads it directly.

### Key Systems

**Actions:** Defined in `game_data.json` under `actions`. Each action has optional `cost`, `effects`, `message`, `add_intel`, `advance_time`. Use `message_after_heist` for conditional messages.

**Dialogues:** Arrays of `{speaker, text, choices?}`. Use `{player_name}` placeholder for dynamic names. Choices have `{text, effect}` where effect modifies stats/flags.

**Flags:** Track story progress (`met_cal`, `accepted_heist`, etc.) and visited locations (`visited_grocery`, etc.).

**Heist System:** Three phases (infiltration, calling_card, escape) with stat-based options. Each option has `stat`, `req` (requirement), and `success` outcome.

### HTML-Specific (index.html)

- `enterLocation(locationId)` - Handles location entry and story triggers
- `doLocationAction(locationId, action)` - Processes actions using GAME_DATA
- `playDialogue(dialogue, callback)` - Runs dialogue sequences
- Sidebar fixed at 250px right, dialogue box at z-index 600

### Python-Specific (game.py)

- `visit_location(location_id)` - Location handling with story triggers
- `handle_location_action(location_id, action)` - Action processing
- `play_dialogue_sequence(dialogue_key)` - Dialogue playback

## Adding Content

1. Add to `game_data.json` (use snake_case for keys)
2. Run `python3 build.py` to update HTML
3. Both versions will use the new content

## Story Flow

Chapter 1: Museum Heist (The Jade Whip)
1. Clinic → Meet Cal → Unlock underground market
2. Underground → Accept heist → Get equipment
3. Museum → Scout → Meet Inspector Mori
4. Underground → Begin heist (requires intel)
5. Three-phase heist with stat checks
