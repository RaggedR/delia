#!/usr/bin/env python3
"""
PhantomThrill - A Text-Based Phantom Thief Adventure
Game data loaded from game_data.json
"""

import json
import os
import time
import copy
import random

# Load game data from JSON
GAME_DATA_FILE = os.path.join(os.path.dirname(__file__), "game_data.json")
SAVE_FILE = os.path.join(os.path.dirname(__file__), "phantomthrill_save.json")

with open(GAME_DATA_FILE, 'r') as f:
    GAME_DATA = json.load(f)

# Game State (will be initialized from GAME_DATA)
game_state = None


def init_game_state():
    """Initialize game state from game_data.json."""
    global game_state
    game_state = copy.deepcopy(GAME_DATA["initial_state"])


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def slow_print(text, delay=0.02):
    """Print text with a typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_divider():
    print("=" * 60)


def print_stats():
    """Display current stats."""
    s = game_state["stats"]
    print_divider()
    print(f"Day {game_state['day']} - {game_state['time_of_day']}")
    print(f"Money: ${s['money']} | Hunger: {s['hunger']}% | Health: {s['health']}%")
    print(f"Charisma: {s['charisma']} | Fitness: {s['fitness']} | Knowledge: {s['knowledge']} | Criminality: {s['criminality']}")
    print_divider()


def get_choice(options, prompt="Choose an option: "):
    """Get a valid choice from the player."""
    while True:
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        try:
            choice = int(input(f"\n{prompt}"))
            if 1 <= choice <= len(options):
                return choice - 1
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")


def replace_placeholders(text):
    """Replace {player_name} and other placeholders in text."""
    return text.replace("{player_name}", game_state["player"]["name"])


def show_dialogue(speaker, text):
    """Display dialogue."""
    speaker = replace_placeholders(speaker)
    text = replace_placeholders(text)
    print(f"\n[{speaker}]")
    slow_print(f'"{text}"')
    input("\n(Press Enter to continue...)")


def show_narration(text):
    """Display narration."""
    text = replace_placeholders(text)
    print()
    slow_print(text)
    input("\n(Press Enter to continue...)")


def apply_effect(effect):
    """Apply an effect from a choice."""
    for key, value in effect.items():
        if key in game_state["stats"]:
            game_state["stats"][key] = min(100, game_state["stats"][key] + value)
            print(f"\n(+{value} {key.capitalize()})")
        elif key == "flag":
            game_state["flags"][value] = True
        elif key == "suspicion":
            game_state["heist"]["suspicion"] += value
        elif key == "ending":
            show_ending(value)


def play_dialogue_sequence(dialogue_key):
    """Play a dialogue sequence from game data."""
    dialogue = GAME_DATA["dialogues"].get(dialogue_key, [])

    for line in dialogue:
        speaker = replace_placeholders(line["speaker"])
        text = replace_placeholders(line["text"])

        if "choices" in line:
            print(f"\n[{speaker}]")
            slow_print(f'"{text}"')

            print("\nHow do you respond?")
            choice_texts = [c["text"] for c in line["choices"]]
            choice_idx = get_choice(choice_texts)

            chosen = line["choices"][choice_idx]
            if "effect" in chosen:
                apply_effect(chosen["effect"])
        else:
            if speaker == "Narrator":
                show_narration(text)
            else:
                show_dialogue(speaker, text)


def advance_time():
    """Advance time of day."""
    times = ["Morning", "Afternoon", "Evening", "Night"]
    current_index = times.index(game_state["time_of_day"])

    if current_index == len(times) - 1:
        game_state["day"] += 1
        game_state["time_of_day"] = "Morning"
    else:
        game_state["time_of_day"] = times[current_index + 1]

    # Decay stats
    game_state["stats"]["hunger"] = max(0, game_state["stats"]["hunger"] - 5)
    game_state["stats"]["hygiene"] = max(0, game_state["stats"]["hygiene"] - 3)

    # Check for game over
    if game_state["stats"]["hunger"] <= 0:
        show_ending("starvation")
    if game_state["stats"]["health"] <= 0:
        show_ending("health")


def show_ending(ending_key):
    """Handle game ending."""
    ending = GAME_DATA["endings"].get(ending_key, {"title": "The End", "text": "Game Over"})
    clear_screen()
    print_divider()
    print(ending["title"].upper())
    print_divider()
    print(ending["text"])
    print_divider()

    if ending_key == "chapter1_complete":
        game_state["stats"]["money"] += 5000
        game_state["stats"]["criminality"] = min(100, game_state["stats"]["criminality"] + 20)
        game_state["flags"]["completed_museum_heist"] = True
        print(f"\nYou earned $5000! Total: ${game_state['stats']['money']}")
        input("Press Enter to continue...")
    else:
        input("Press Enter to exit...")
        exit()


def save_game():
    """Save game to file."""
    with open(SAVE_FILE, 'w') as f:
        json.dump(game_state, f)
    print("Game saved!")


def load_game():
    """Load game from file."""
    global game_state
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            game_state = json.load(f)
        return True
    return False


def intro_sequence():
    """Play the intro sequence."""
    clear_screen()
    print_divider()
    print(GAME_DATA["meta"]["title"].upper())
    print(GAME_DATA["meta"]["subtitle"])
    print_divider()

    name = input("\nEnter your name (default: Alex): ").strip() or "Alex"
    thief_name = input("Enter your thief alias (default: Thrill): ").strip() or "Thrill"

    game_state["player"]["name"] = name
    game_state["player"]["thief_name"] = thief_name

    clear_screen()
    play_dialogue_sequence("intro")


def clinic_meet_cal():
    """Cal meeting sequence at the clinic."""
    play_dialogue_sequence("clinic_meet_cal")

    game_state["flags"]["met_cal"] = True
    game_state["flags"]["found_underground"] = True
    print("\n*** The Underground Market is now accessible! ***")
    input("Press Enter to continue...")


def underground_first():
    """First visit to underground market."""
    play_dialogue_sequence("underground_first")

    if game_state["flags"].get("accepted_heist"):
        play_dialogue_sequence("accept_heist")
        game_state["inventory"].append("Burner Phone")
        game_state["inventory"].append("Disguise Kit")
        print("\n*** Received: Burner Phone, Disguise Kit ***")
        print("*** Objective: Scout the City Museum ***")
        input("Press Enter to continue...")


def museum_scout():
    """Museum scouting sequence."""
    play_dialogue_sequence("museum_scout")

    game_state["flags"]["got_jade_whip_info"] = True
    game_state["heist"]["intel"].append("Jade Whip location: East Wing")
    print("\n*** Intel gathered: Jade Whip location ***")
    input("Press Enter to continue...")


def inspector_meet():
    """Meeting Inspector Mori."""
    play_dialogue_sequence("inspector_meet")

    game_state["flags"]["met_inspector"] = True
    print("\n*** Objective: Return to the underground market when ready for the heist ***")
    input("Press Enter to continue...")


def run_heist():
    """Run the museum heist."""
    clear_screen()
    print_divider()
    print("THE MUSEUM HEIST BEGINS")
    print_divider()
    print_stats()
    input("Press Enter to start...")

    heist_data = GAME_DATA["heist_sequences"]["museum"]
    phases = ["infiltration", "calling_card", "escape"]
    phase_names = ["INFILTRATION", "CALLING CARD", "ESCAPE"]

    for phase_idx, phase in enumerate(phases):
        clear_screen()
        print_divider()
        print(f"PHASE {phase_idx + 1}: {phase_names[phase_idx]}")
        print_divider()

        scenes = heist_data[phase]

        for scene in scenes:
            print(f"\n{scene['icon']} {scene['description']}")
            print("\nYour options:")

            options = scene["options"]
            for i, opt in enumerate(options, 1):
                stat_val = game_state["stats"][opt["stat"]]
                status = "OK" if stat_val >= opt["req"] else "FAIL"
                print(f"  {i}. {opt['text']} ({opt['stat'].capitalize()} {opt['req']}+) [{status}: {stat_val}]")

            choice = get_choice([opt["text"] for opt in options], "Choose your approach: ")
            chosen = options[choice]

            stat_val = game_state["stats"][chosen["stat"]]
            if stat_val >= chosen["req"]:
                print(f"\n*** SUCCESS! Your {chosen['stat']} ({stat_val}) met the requirement ({chosen['req']})! ***")
                input("Press Enter to continue...")
            else:
                print(f"\n*** FAILED! Your {chosen['stat']} ({stat_val}) didn't meet the requirement ({chosen['req']})! ***")
                show_ending("caught")

    # Victory!
    show_ending("chapter1_complete")


def handle_location_action(location_id, action):
    """Handle actions at locations."""
    stats = game_state["stats"]
    action_data = GAME_DATA["actions"].get(action)

    if action_data:
        # Check cost
        cost = action_data.get("cost", 0)
        if cost > 0:
            if stats["money"] >= cost:
                stats["money"] -= cost
            else:
                print("\nNot enough money!")
                input("\nPress Enter to continue...")
                return False

        # Apply effects
        effects = action_data.get("effects", {})
        for stat, value in effects.items():
            if value == "full":
                stats[stat] = 100
            elif stat in stats:
                stats[stat] = min(100, max(0, stats[stat] + value))

        # Add intel if specified
        intel = action_data.get("add_intel")
        if intel and intel not in game_state["heist"]["intel"]:
            game_state["heist"]["intel"].append(intel)

        # Advance time if specified
        if action_data.get("advance_time"):
            advance_time()

        print(f"\n{action_data.get('message', 'Done.')}")
        input("\nPress Enter to continue...")
        return False

    # Handle special actions
    if action == "Talk to receptionist":
        if not game_state["flags"]["met_cal"]:
            clinic_meet_cal()
            return True

    elif action == "Talk to dealer":
        if game_state["flags"].get("accepted_heist") and game_state["flags"].get("got_jade_whip_info"):
            print("\nReady to start the heist?")
            choice = get_choice(["Yes, let's do this!", "Not yet, I need to prepare more."])
            if choice == 0:
                run_heist()
                return True
        elif not game_state["flags"].get("accepted_heist"):
            underground_first()
            return True
        else:
            print("\n\"Scout the museum first, then come back.\"")
            input("\nPress Enter to continue...")

    elif action == "Check wanted posters":
        # Special case: message changes after completing heist
        action_data = GAME_DATA['actions']['Check wanted posters']
        if game_state["flags"].get("completed_museum_heist"):
            print(f"\n{action_data.get('message_after_heist', action_data['message'])}")
        else:
            print(f"\n{action_data['message']}")
        input("\nPress Enter to continue...")

    return False


def is_location_unlocked(location_id):
    """Check if a location is unlocked."""
    loc = GAME_DATA["locations"].get(location_id, {})
    if not loc.get("locked", False):
        return True

    unlock_flag = loc.get("unlock_flag")
    if unlock_flag and game_state["flags"].get(unlock_flag):
        return True

    return False


def visit_location(location_id):
    """Visit a location and handle events."""
    loc = GAME_DATA["locations"].get(location_id)
    if not loc:
        return

    # Check for locked locations
    if not is_location_unlocked(location_id):
        print("\nThis location is not accessible yet.")
        input("Press Enter to continue...")
        return

    game_state["current_location"] = location_id

    # Story triggers
    if location_id == "clinic" and not game_state["flags"]["met_cal"]:
        clinic_meet_cal()
        return

    if location_id == "underground" and not game_state["flags"].get("accepted_heist"):
        underground_first()
        return

    if location_id == "museum" and game_state["flags"].get("accepted_heist") and not game_state["flags"].get("got_jade_whip_info"):
        museum_scout()
        if not game_state["flags"].get("met_inspector"):
            inspector_meet()
        return

    # Check for first-time location visits (side adventures)
    location_dialogue_map = {
        "grocery": {"flag": "visited_grocery", "dialogue": "grocery_visit"},
        "mall": {"flag": "visited_mall", "dialogue": "mall_visit"},
        "restaurant": {"flag": "visited_restaurant", "dialogue": "restaurant_visit"},
        "gym": {"flag": "visited_gym", "dialogue": "gym_visit"},
        "bar": {"flag": "visited_bar", "dialogue": "bar_visit"},
        "police": {"flag": "visited_police", "dialogue": "police_visit"},
        "motel": {"flag": "visited_motel", "dialogue": "motel_return"}
    }

    loc_info = location_dialogue_map.get(location_id)
    if loc_info and not game_state["flags"].get(loc_info["flag"]):
        dialogue_key = loc_info["dialogue"]
        if dialogue_key in GAME_DATA["dialogues"]:
            game_state["flags"][loc_info["flag"]] = True
            clear_screen()
            print_stats()
            print(f"\n{loc['icon']} === {loc['name']} ===")
            play_dialogue_sequence(dialogue_key)

    # Normal location visit
    while True:
        clear_screen()
        print_stats()
        print(f"\n{loc['icon']} === {loc['name']} ===")
        print(loc['description'])

        # Build actions list
        actions = loc["actions"].copy()

        # Add heist option if ready
        if location_id == "underground" and game_state["flags"].get("accepted_heist") and game_state["flags"].get("got_jade_whip_info"):
            actions.insert(0, "*** BEGIN MUSEUM HEIST ***")

        actions.append("Leave")

        print("\nWhat do you do?")
        choice = get_choice(actions)
        action = actions[choice]

        if action == "Leave":
            break
        elif action == "*** BEGIN MUSEUM HEIST ***":
            run_heist()
            break
        else:
            if handle_location_action(location_id, action):
                break


def show_inventory():
    """Show inventory."""
    print("\n=== INVENTORY ===")
    if not game_state["inventory"]:
        print("No items yet.")
    else:
        for item in game_state["inventory"]:
            print(f"  - {item}")
    input("\nPress Enter to continue...")


def show_intel():
    """Show gathered intel."""
    print("\n=== INTEL NOTES ===")
    if not game_state["heist"]["intel"]:
        print("No intel yet. Scout locations!")
    else:
        for note in game_state["heist"]["intel"]:
            print(f"  - {note}")
    input("\nPress Enter to continue...")


def main_menu():
    """Show the main game menu."""
    while True:
        clear_screen()
        print_stats()

        print("\n=== LOCATIONS ===")
        available = []
        for loc_id, loc in GAME_DATA["locations"].items():
            if is_location_unlocked(loc_id):
                available.append((loc_id, loc["name"], loc["icon"]))

        for i, (loc_id, name, icon) in enumerate(available, 1):
            marker = " (YOU ARE HERE)" if loc_id == game_state["current_location"] else ""
            print(f"  {i}. {icon} {name}{marker}")

        print(f"\n  {len(available) + 1}. View Inventory")
        print(f"  {len(available) + 2}. View Intel Notes")
        print(f"  {len(available) + 3}. Save Game")
        print(f"  {len(available) + 4}. Quit")

        try:
            choice = int(input("\nWhere do you want to go? "))
            if 1 <= choice <= len(available):
                visit_location(available[choice - 1][0])
            elif choice == len(available) + 1:
                show_inventory()
            elif choice == len(available) + 2:
                show_intel()
            elif choice == len(available) + 3:
                save_game()
                input("Press Enter to continue...")
            elif choice == len(available) + 4:
                save_game()
                print("Thanks for playing!")
                break
        except ValueError:
            pass


def title_screen():
    """Show title screen."""
    clear_screen()
    print_divider()
    print(r"""
    ____  _                 _                 _____ _          _ _ _
   |  _ \| |__   __ _ _ __ | |_ ___  _ __ ___|_   _| |__  _ __(_) | |
   | |_) | '_ \ / _` | '_ \| __/ _ \| '_ ` _ \ | | | '_ \| '__| | | |
   |  __/| | | | (_| | | | | || (_) | | | | | || | | | | | |  | | | |
   |_|   |_| |_|\__,_|_| |_|\__\___/|_| |_| |_||_| |_| |_|_|  |_|_|_|

    """)
    print(f"                    {GAME_DATA['meta']['subtitle']}")
    credits = GAME_DATA['meta']['credits']
    print(f"\n           {credits['game_designer']} (Designer) | {credits['prompter']} (Prompter)")
    print(f"                      {credits['software_engineer']} (Engineer)")
    print_divider()
    print()

    choice = get_choice(["New Game", "Continue", "Quit"])

    if choice == 0:
        init_game_state()
        intro_sequence()
        main_menu()
    elif choice == 1:
        if load_game():
            print("\nGame loaded!")
            input("Press Enter to continue...")
            main_menu()
        else:
            print("\nNo save file found. Starting new game...")
            input("Press Enter to continue...")
            init_game_state()
            intro_sequence()
            main_menu()
    else:
        print("\nGoodbye!")


if __name__ == "__main__":
    title_screen()
