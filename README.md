# PhantomThrill

A visual novel / life-sim RPG about a fresh graduate who becomes a phantom thief.

## Play the Game

**Browser version:** Download `index.html` and open it in any browser - no server or installation required.

**Text-based version:**
```bash
python3 game.py
```

## Story

You're a recent graduate drowning in rejection letters. When a chance encounter leads you to the underground world of phantom thieves, you must choose: stay on the struggling straight path, or embrace a life of thrilling heists?

Balance daily life - eating, working out, building skills - while preparing for your first big job: stealing the legendary Jade Whip from the City Museum. But beware of Inspector Mori, who's always one step behind...

## Features

- Stat-based gameplay (Charisma, Fitness, Knowledge, Criminality)
- Multiple paths through heists based on your build
- Story choices that affect relationships and outcomes
- Day/night cycle with time management
- Save/load system

## Credits

- **Game Designer:** Celia Kok
- **Prompter:** Robin Langer
- **Software Engineer:** Claude Code

Inspired by Miami Nights 2, Persona, and Ace Attorney.

## Development

Game data is stored in `game_data.json`. After editing, run:
```bash
python3 build.py
```
This updates the browser version with the new content.
