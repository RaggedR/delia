#!/usr/bin/env python3
"""
Build script that embeds game_data.json into index.html
Run this after editing game_data.json to update the HTML version.
"""

import json
import re
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DATA_FILE = os.path.join(SCRIPT_DIR, "game_data.json")
HTML_FILE = os.path.join(SCRIPT_DIR, "index.html")


def convert_to_js_key(key):
    """Convert snake_case to camelCase."""
    components = key.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_keys_to_camel_case(obj):
    """Recursively convert all keys from snake_case to camelCase."""
    if isinstance(obj, dict):
        return {convert_to_js_key(k): convert_keys_to_camel_case(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_camel_case(item) for item in obj]
    else:
        return obj


def main():
    # Load game data
    with open(GAME_DATA_FILE, 'r') as f:
        game_data = json.load(f)

    # Convert to camelCase for JavaScript
    game_data_js = convert_keys_to_camel_case(game_data)

    # Read current HTML
    with open(HTML_FILE, 'r') as f:
        html = f.read()

    # Check if GAME_DATA marker exists
    marker_start = "// === GAME_DATA_START ==="
    marker_end = "// === GAME_DATA_END ==="

    if marker_start in html:
        # Replace existing GAME_DATA
        pattern = re.compile(
            re.escape(marker_start) + r".*?" + re.escape(marker_end),
            re.DOTALL
        )
        game_data_block = f"""{marker_start}
        const GAME_DATA = {json.dumps(game_data_js, indent=8)};
        {marker_end}"""
        # Use lambda to avoid backslash interpretation in replacement string
        html = pattern.sub(lambda m: game_data_block, html)
        print("Updated existing GAME_DATA in index.html")
    else:
        # Insert GAME_DATA after <script> tag
        script_tag = "<script>"
        insert_pos = html.find(script_tag) + len(script_tag)
        game_data_block = f"""
        {marker_start}
        const GAME_DATA = {json.dumps(game_data_js, indent=8)};
        {marker_end}
        """
        html = html[:insert_pos] + game_data_block + html[insert_pos:]
        print("Inserted GAME_DATA into index.html")

    # Write updated HTML
    with open(HTML_FILE, 'w') as f:
        f.write(html)

    print(f"Successfully updated {HTML_FILE} with data from {GAME_DATA_FILE}")


if __name__ == "__main__":
    main()
