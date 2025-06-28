import json
import threading
import time
import uuid
import os
import logging
import mmap
import pickle
from multiprocessing import Lock as ProcessLock, shared_memory
from typing import Dict, Optional, Any

class GameStateManager:
    """
    Thread-safe singleton class for managing game states with shared memory for multiprocess support.
    """
    _instance = None
    _lock = threading.Lock()
    _shared_memory_name = "werewolf_game_state"
    _shared_memory_size = 1024 * 1024 * 10  # 10MB shared memory
    
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
            self.process_lock = ProcessLock()  # For multiprocess synchronization
            self.shared_mem = None
            self._init_shared_memory()
            self.load_from_shared_memory()
            self.initialized = True
    
    def _init_shared_memory(self):
        """Initialize shared memory for multiprocess communication."""
        try:
            # Try to connect to existing shared memory
            self.shared_mem = shared_memory.SharedMemory(name=self._shared_memory_name)
            logging.info("Connected to existing shared memory")
        except FileNotFoundError:
            # Create new shared memory if it doesn't exist
            try:
                self.shared_mem = shared_memory.SharedMemory(
                    name=self._shared_memory_name, 
                    create=True, 
                    size=self._shared_memory_size
                )
                # Initialize with empty data
                self._write_to_shared_memory({})
                logging.info("Created new shared memory")
            except Exception as e:
                logging.error(f"Failed to create shared memory: {e}")
                # Fallback to file-based storage
                self.shared_mem = None
        except Exception as e:
            logging.error(f"Failed to connect to shared memory: {e}")
            # Fallback to file-based storage
            self.shared_mem = None
    
    def _write_to_shared_memory(self, data: Dict):
        """Write data to shared memory."""
        if not self.shared_mem:
            return False
        
        try:
            # Serialize data using pickle
            serialized_data = pickle.dumps(data)
            data_size = len(serialized_data)
            
            if data_size > self._shared_memory_size - 8:  # Reserve 8 bytes for size header
                logging.error(f"Data too large for shared memory: {data_size} bytes")
                return False
            
            # Write size header (first 8 bytes) then data
            self.shared_mem.buf[:8] = data_size.to_bytes(8, byteorder='little')
            self.shared_mem.buf[8:8 + data_size] = serialized_data
            
            return True
        except Exception as e:
            logging.error(f"Error writing to shared memory: {e}")
            return False
    
    def _read_from_shared_memory(self) -> Dict:
        """Read data from shared memory."""
        if not self.shared_mem:
            return {}
        
        try:
            # Read size header (first 8 bytes)
            data_size = int.from_bytes(self.shared_mem.buf[:8], byteorder='little')
            
            if data_size == 0:
                return {}
            
            if data_size > self._shared_memory_size - 8:
                logging.error(f"Invalid data size in shared memory: {data_size}")
                return {}
            
            # Read serialized data
            serialized_data = bytes(self.shared_mem.buf[8:8 + data_size])
            return pickle.loads(serialized_data)
            
        except Exception as e:
            logging.error(f"Error reading from shared memory: {e}")
            return {}
    
    def load_from_shared_memory(self):
        """Load game states from shared memory, with file fallback."""
        with self.process_lock:
            if self.shared_mem:
                shared_data = self._read_from_shared_memory()
                if shared_data:
                    with self.games_lock:
                        self.games = shared_data
                    return
            
            # Fallback to file loading
            self.load_from_file()
            
            # If we loaded from file and have shared memory, sync it
            if self.shared_mem and self.games:
                self._write_to_shared_memory(self.games)
    
    def save_to_shared_memory(self):
        """Save game states to shared memory and file backup."""
        with self.process_lock:
            # Save to shared memory
            if self.shared_mem:
                self._write_to_shared_memory(self.games)
            
            # Also save to file as backup
            self.save_to_file()
    
    def create_game(self) -> str:
        """Create a new game and return its ID."""
        self.load_from_shared_memory()
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
        
        self.save_to_shared_memory()
        return game_id
    
    def add_player(self, game_id: str, name: str) -> Optional[str]:
        """Add a player to the game and return their player ID."""
        self.load_from_shared_memory()  # Ensure we have the latest game state
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
        
        self.save_to_shared_memory()
        return player_id
    
    def get_game_state(self, game_id: str) -> Optional[Dict]:
        """Get the current state of a game."""
        self.load_from_shared_memory()  # Ensure we have the latest game state
        with self.games_lock:
            return self.games.get(game_id, None)
    
    def update_game_state(self, game_id: str, updates: Dict) -> bool:
        """Update game state with given updates."""
        self.load_from_shared_memory()
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
        
        self.save_to_shared_memory()
        return True
    
    def record_action(self, game_id: str, action_type: str, player_id: str, target_id: str = None, data: Any = None) -> bool:
        """Record a player action."""
        self.load_from_shared_memory()
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
        
        self.save_to_shared_memory()
        return True
    
    def add_chat_message(self, game_id: str, player_id: str, message: str) -> bool:
        """Add a chat message to the game."""
        self.load_from_shared_memory()
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
        
        self.save_to_shared_memory()
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
        self.load_from_shared_memory()
        with self.games_lock:
            return dict(self.games)
    
    def cleanup_old_games(self, max_age_hours: int = 24):
        """Remove games older than specified hours."""
        self.load_from_shared_memory()
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
            self.save_to_shared_memory()
        
        return len(games_to_remove)
    
    def cleanup_shared_memory(self):
        """Clean up shared memory resources when shutting down."""
        if self.shared_mem:
            try:
                self.shared_mem.close()
                self.shared_mem.unlink()  # Remove the shared memory
                logging.info("Cleaned up shared memory")
            except Exception as e:
                logging.error(f"Error cleaning up shared memory: {e}")
    
    def __del__(self):
        """Destructor to clean up resources."""
        if hasattr(self, 'shared_mem') and self.shared_mem:
            try:
                self.shared_mem.close()
            except Exception as e:
                logging.error(f"Error closing shared memory in destructor: {e}")
