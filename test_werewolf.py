#!/usr/bin/env python3
"""
Test script for the Werewolf Game Server using only standard library.
This script demonstrates the complete game flow.
"""

import json
import urllib.request
import urllib.parse
import time

BASE_URL = "http://localhost:8888"

def make_request(method, endpoint, data=None):
    """Make a request to the server using urllib."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            with urllib.request.urlopen(url) as response:
                result = json.loads(response.read().decode())
                print(f"GET {endpoint}")
                print(f"Status: {response.getcode()}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
                
        elif method == 'POST':
            headers = {'Content-Type': 'application/json'}
            if data:
                data_encoded = json.dumps(data).encode('utf-8')
            else:
                data_encoded = b''
            
            req = urllib.request.Request(url, data=data_encoded, headers=headers, method='POST')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                print(f"POST {endpoint}")
                if data:
                    print(f"Request: {json.dumps(data, indent=2)}")
                print(f"Status: {response.getcode()}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
        
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_game_flow():
    """Test the complete game flow."""
    print("=== Werewolf Game Server Test ===\n")
    
    # 1. Create a new game
    print("1. Creating a new game...")
    game_data = make_request('POST', '/games')
    if not game_data or 'game_id' not in game_data:
        print("Failed to create game")
        return
    
    game_id = game_data['game_id']
    print(f"Game created with ID: {game_id}\n")
    
    # 2. Add players
    players = []
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana']
    
    print("2. Adding players...")
    for name in player_names:
        player_data = make_request('POST', f'/games/{game_id}/join', {'name': name})
        if player_data and 'player_id' in player_data:
            players.append({
                'name': name,
                'id': player_data['player_id']
            })
            print(f"Player {name} joined with ID: {player_data['player_id']}")
    print()
    
    # 3. Get game state before starting
    print("3. Game state before starting...")
    make_request('GET', f'/games/{game_id}/state')
    print()
    
    # 4. Start the game
    print("4. Starting the game...")
    make_request('POST', f'/games/{game_id}/start')
    print()
    
    # 5. Get game state after starting
    print("5. Game state after starting...")
    state = make_request('GET', f'/games/{game_id}/state')
    print()
    
    # 6. Get player role information
    print("6. Player role information...")
    for player in players:
        print(f"\nRole info for {player['name']}:")
        make_request('GET', f'/games/{game_id}/player/{player["id"]}')
    print()
    
    print("=== Test completed ===")
    print("Note: For full testing including phase transitions, let the server run")
    print("and observe the automatic phase changes after 2 minutes (night) and 5 minutes (day)")
    print()
    print("=== API Documentation Endpoints ===")
    print("Test the API documentation:")
    
    # Test API docs endpoints
    print("\n7. Testing API documentation endpoints...")
    print("API Documentation (JSON):")
    make_request('GET', '/api-docs')
    print("\nSwagger UI should be available at: http://localhost:8888/swagger-ui")
    print("OpenAPI YAML at: http://localhost:8888/api-docs.yaml")

if __name__ == '__main__':
    print("Make sure the server is running with: python main.py")
    print("Then run this test script in another terminal.\n")
    
    # Test the game flow
    test_game_flow()
