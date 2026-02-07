import argparse
import sys
import json
import os
import random

# Adjust path to allow imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pr_agent.client import OllamaClient
from pr_agent.prompts import get_messages
from pr_agent.search import get_random_quote_context

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def main():
    parser = argparse.ArgumentParser(description="PR Message Generator with Character Persona")
    parser.add_argument("command", choices=["pr", "merge"], help="Command to execute")
    parser.add_argument("--input", "-i", type=str, help="Input text (diff or summary). Should be piped if large.")
    parser.add_argument("--character", "-c", type=str, help="Character name or index to use (default: active character)")

    args = parser.parse_args()
    
    # Load Config
    try:
        with open(CONFIG_PATH, "r", encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        return
    
    # Get characters
    characters = config.get("characters", [])
    if not characters:
        print("Error: No characters defined in config.json")
        return
    
    # Select character
    if args.character:
        # Try to find by name first
        character_config = None
        for char in characters:
            if char.get("name", "").lower() == args.character.lower():
                character_config = char
                break
        
        # Try by index
        if not character_config:
            try:
                idx = int(args.character)
                if 0 <= idx < len(characters):
                    character_config = characters[idx]
            except ValueError:
                pass
        
        if not character_config:
            print(f"Error: Character '{args.character}' not found")
            return
    else:
        # Use active character
        active_index = config.get("active_character_index", 0)
        if active_index >= len(characters):
            active_index = 0
        character_config = characters[active_index]
    
    char_name = character_config.get("name", "Unknown")
    work_name = character_config.get("work", "Unknown")

    # Read input from stdin if not provided
    input_text = args.input
    if not input_text:
        # Check if piped input is available
        if not sys.stdin.isatty():
             input_text = sys.stdin.read()
        else:
             print("Error: No input provided. Pipe a diff or use --input.")
             return

    # Initialize Client
    client = OllamaClient(api_url=config["api_url"], model=config["model"])
    
    print(f"Generating {args.command.upper()} message as {char_name} ({work_name})...")
    
    # Step: Search for character quotes if enabled
    search_context = ""
    if config.get("use_search", False) and char_name:
        print(f"Searching quotes for character: {char_name}...")
        try:
            search_context = get_random_quote_context(char_name, work_name)
        except Exception as e:
            print(f"Search failed: {e}")

    # Customize prompt slightly based on command
    if args.command == "merge":
        input_text = f"This is a MERGE request. Input details: {input_text}"
    else:
        input_text = f"This is a PULL REQUEST. Input changes: {input_text}"

    target_length = config.get("target_length", 300)
    prompt = get_messages(character_config, input_text, search_context, target_length=target_length)
    
    try:
        response = client.generate_text(prompt)
        print("\n=== GENERATED MESSAGE ===\n")
        print(response)
        print("\n=========================\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
