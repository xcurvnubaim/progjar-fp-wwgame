import json
import threading
import time
import uuid
import os
import logging
from typing import Dict, Optional, Any

class GameStateManager:
    """
    Thread-safe singleton class for managing game states with file persistence.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.games: Dict[str, Dict] = {}
            self.file_path = 'game_states.json'
            self.file_lock = threading.Lock()
            self.games_lock = threading.Lock()
            self.load_from_file()
            self.initialized = True
    
    def create_game(self) -> str:
        """Create a new game and return its ID."""
        self.load_from_file()
        game_id = str(uuid.uuid4())[:8]  # Short ID for easier use
        
        with self.games_lock:
            self.games[game_id] = {
                'phase': 'setup',
                'phase_end': None,
                'players': {},
                'actions': {
                    'werewolf_votes': {},
                    'seer_target': None,
                    'day_votes': {}
                },
                'seer_history': [],
                'chat': [],
                'created_at': time.time(),
                'started': False,
                'ended': False,
                'winner': None
            }
        
        self.save_to_file()
        return game_id
    
    def add_player(self, game_id: str, name: str) -> Optional[str]:
        """Add a player to the game and return their player ID."""
        self.load_from_file()  # Ensure we have the latest game state
        if game_id not in self.games:
            return None
        
        with self.games_lock:
            game = self.games[game_id]
            if game['started'] or game['ended']:
                return None
            
            # Check if name already exists
            for player in game['players'].values():
                if player['name'] == name:
                    return None
            
            player_id = str(uuid.uuid4())[:8]
            game['players'][player_id] = {
                'name': name,
                'role': None,
                'alive': True,
                'vote': None,
                'joined_at': time.time()
            }
        
        self.save_to_file()
        return player_id
    
    def get_game_state(self, game_id: str) -> Optional[Dict]:
        """Get the current state of a game."""
        self.load_from_file()  # Ensure we have the latest game state
        with self.games_lock:
            return self.games.get(game_id, None)
    
    def update_game_state(self, game_id: str, updates: Dict) -> bool:
        """Update game state with given updates."""
        self.load_from_file()
        if game_id not in self.games:
            return False
        
        with self.games_lock:
            for key, value in updates.items():
                if key in self.games[game_id]:
                    if isinstance(value, dict) and isinstance(self.games[game_id][key], dict):
                        logging.warning("Updating existing key: %s in game %s with value %s", key, game_id, value)
                        self.games[game_id][key].update(value)
                    else:
                        logging.warning("Setting key: %s in game %s to value %s", key, game_id, value)
                        self.games[game_id][key] = value

        logging.warning(f'{self.games[game_id]}, {game_id}, {updates}')
        
        self.save_to_file()
        return True
    
    def record_action(self, game_id: str, action_type: str, player_id: str, target_id: str = None, data: Any = None) -> bool:
        """Record a player action."""
        self.load_from_file()
        if game_id not in self.games:
            return False
        
        with self.games_lock:
            game = self.games[game_id]
            
            if action_type == 'werewolf_vote':
                if target_id not in game['actions']['werewolf_votes']:
                    game['actions']['werewolf_votes'][target_id] = 0
                game['actions']['werewolf_votes'][target_id] += 1
                
            elif action_type == 'seer_investigate':
                game['actions']['seer_target'] = target_id
                
            elif action_type == 'day_vote':
                # Clear previous vote
                for target, votes in game['actions']['day_votes'].items():
                    if player_id in votes:
                        votes.remove(player_id)
                        if not votes:
                            del game['actions']['day_votes'][target]
                        break
                
                # Add new vote
                if target_id not in game['actions']['day_votes']:
                    game['actions']['day_votes'][target_id] = []
                game['actions']['day_votes'][target_id].append(player_id)
                
                # Update player vote
                game['players'][player_id]['vote'] = target_id
        
        self.save_to_file()
        return True
    
    def add_chat_message(self, game_id: str, player_id: str, message: str) -> bool:
        """Add a chat message to the game."""
        self.load_from_file()
        if game_id not in self.games:
            return False
        
        with self.games_lock:
            game = self.games[game_id]
            
            # Rate limiting: max 3 messages per player per minute
            current_time = time.time()
            recent_messages = [
                msg for msg in game['chat']
                if msg['player'] == player_id and (current_time - msg['time']) < 60
            ]
            
            if len(recent_messages) >= 3:
                return False
            
            # Sanitize message
            sanitized_message = message.strip()[:200]  # Max 200 chars
            if not sanitized_message:
                return False
            
            game['chat'].append({
                'player': player_id,
                'message': sanitized_message,
                'time': current_time
            })
        
        self.save_to_file()
        return True
    
    def save_to_file(self):
        """Save game states to file with atomic write."""
        with self.file_lock:
            temp_file = self.file_path + '.tmp'
            try:
                with open(temp_file, 'w') as f:
                    json.dump(self.games, f, indent=2)
                
                # Atomic move
                if os.name == 'nt':  # Windows
                    if os.path.exists(self.file_path):
                        os.remove(self.file_path)
                    os.rename(temp_file, self.file_path)
                else:  # Unix
                    os.rename(temp_file, self.file_path)
                    
            except Exception as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                print(f"Error saving game state: {e}")
    
    def load_from_file(self):
        """Load game states from file."""
        with self.file_lock:
            if os.path.exists(self.file_path):
                try:
                    with open(self.file_path, 'r') as f:
                        loaded_games = json.load(f)
                    
                    with self.games_lock:
                        self.games = loaded_games
                        
                except Exception as e:
                    print(f"Error loading game state: {e}")
                    self.games = {}
            else:
                self.games = {}
    
    def get_all_games(self) -> Dict[str, Dict]:
        """Get all games (for debugging/admin purposes)."""
        self.load_from_file()
        with self.games_lock:
            return dict(self.games)
    
    def cleanup_old_games(self, max_age_hours: int = 24):
        """Remove games older than specified hours."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self.games_lock:
            games_to_remove = [
                game_id for game_id, game in self.games.items()
                if game.get('created_at', 0) < cutoff_time
            ]
            
            for game_id in games_to_remove:
                del self.games[game_id]
        
        if games_to_remove:
            self.save_to_file()
        
        return len(games_to_remove)
