from pathlib import Path
import json
from typing import List

THIS_DIR = Path(__file__).parent
# Adjusted path for cities.json to be in the same directory as the script
# If cities.json is truly in the parent directory, your original path is fine.
# I'm assuming it's in the same directory for simplicity here,
# based on common project structures where a script might be alongside its data.
# If it's in a sibling directory (like 'data/cities.json' and your script is in 'scripts/'),
# then THIS_DIR / "../cities.json" or THIS_DIR.parent / "cities.json" would be correct.
# Given the example in the prompt, let's stick to your original:
CITIES_JSON_FPATH = THIS_DIR / "./cities.json"


def is_city_capitol_of_state(city_name: str, state_name: str) -> bool:
    """
    Check if the given city is the capital of the specified state.

    Args:
        city_name (str): The name of the city.
        state_name (str): The name of the state.

    Returns:
        bool: True if the city is the capital of the state, False otherwise.
    """
    try:
        cities_json_content = CITIES_JSON_FPATH.read_text(encoding='utf-8')
        cities: List[dict] = json.loads(cities_json_content)
    except FileNotFoundError:
        print(f"Error: cities.json not found at {CITIES_JSON_FPATH}")
        return False
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {CITIES_JSON_FPATH}")
        return False

    # Find the city that matches both the city_name AND the state_name AND is a capital
    # This single loop is more efficient than finding all matching cities
    # and then checking the first one.
    for city_data in cities:
        if city_data["city"] == city_name and \
           city_data["state"] == state_name and \
           city_data["capital"] is True: # Explicitly check the 'capital' boolean
            return True
            
    return False # If no matching capital city is found after checking all entries


if __name__ == "__main__":
    # Ensure you have a cities.json file in the parent directory of your script
    # with content similar to the one I provided in the previous answer.

    # Test cases:
    print(f"Is Bismarck the capital of North Dakota? {is_city_capitol_of_state('Bismarck', 'North Dakota')}") # Should be True
    print(f"Is Phoenix the capital of Arizona? {is_city_capitol_of_state('Phoenix', 'Arizona')}") # Should be True
    print(f"Is New York the capital of New York? {is_city_capitol_of_state('New York', 'New York')}") # Should be False
    print(f"Is Springfield the capital of Illinois? {is_city_capitol_of_state('Springfield', 'Illinois')}") # Should be True
    print(f"Is a non-existent city the capital of a state? {is_city_capitol_of_state('NonExistentCity', 'SomeState')}") # Should be False
    print(f"Is Chicago the capital of Illinois? {is_city_capitol_of_state('Chicago', 'Illinois')}") # Should be False (even if city exists, it's not the capital)