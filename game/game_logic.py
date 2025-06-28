import random
import time
from typing import Dict, List, Optional, Tuple
from game.game_state import GameStateManager

class GameLogic:
    """
    Handles all game rules, role assignments, and phase transitions.
    """
    
    def __init__(self):
        self.state_manager = GameStateManager()
    
    def assign_roles(self, game_id: str) -> bool:
        """
        Randomly assign roles to players in the game.
        1 werewolf, 1 seer, rest villagers (minimum 3 players required).
        """
        game = self.state_manager.get_game_state(game_id)
        if not game or len(game['players']) < 3:
            return False
        
        player_ids = list(game['players'].keys())
        random.shuffle(player_ids)
        
        # Assign roles
        roles = ['werewolf', 'seer'] + ['villager'] * (len(player_ids) - 2)
        
        updates = {}
        for i, player_id in enumerate(player_ids):
            updates[f'players.{player_id}.role'] = roles[i]
        
        # Update game state
        game_updates = {
            'started': True,
            'phase': 'night'
        }
        
        # Apply role assignments
        for player_id, role in zip(player_ids, roles):
            game['players'][player_id]['role'] = role

        game_updates['players'] = game['players']
        
        return self.state_manager.update_game_state(game_id, game_updates)
    
    def resolve_night_actions(self, game_id: str) -> Dict:
        """
        Process night actions: werewolf kills and seer investigations.
        Returns result summary.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game:
            return {'error': 'Game not found'}
        
        result = {
            'killed': None,
            'seer_result': None,
            'actions_processed': True
        }
        
        # Process werewolf votes
        werewolf_votes = game['actions']['werewolf_votes']
        if werewolf_votes:
            # Find most voted target
            most_voted = max(werewolf_votes.items(), key=lambda x: x[1])
            target_id = most_voted[0]
            
            # Kill the target
            if target_id in game['players'] and game['players'][target_id]['alive']:
                game['players'][target_id]['alive'] = False
                result['killed'] = {
                    'player_id': target_id,
                    'name': game['players'][target_id]['name']
                }
        
        # Process seer investigation
        seer_target = game['actions']['seer_target']
        if seer_target and seer_target in game['players']:
            target_role = game['players'][seer_target]['role']
            result['seer_result'] = {
                'target_id': seer_target,
                'target_name': game['players'][seer_target]['name'],
                'is_werewolf': target_role == 'werewolf'
            }
        
        # Clear night actions
        game_updates = {
            'actions': {
                'werewolf_votes': {},
                'seer_target': None,
                'day_votes': {}
            }
        }

        game_updates['seer_history'] = game['seer_history']
        if seer_target:
            game_updates['seer_history'].append({
                'target_id': seer_target,
                'target_role': target_role,
                'timestamp': time.time()
            })

        game_updates['players'] = game['players']
        
        # Clear player votes
        for player in game['players'].values():
            player['vote'] = None
        
        self.state_manager.update_game_state(game_id, game_updates)
        
        return result
    
    def resolve_day_votes(self, game_id: str) -> Dict:
        """
        Process day phase voting and execute the most voted player.
        Returns execution result.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game:
            return {'error': 'Game not found'}
        
        result = {
            'executed': None,
            'vote_counts': {},
            'actions_processed': True
        }
        
        # Count votes
        day_votes = game['actions']['day_votes']
        vote_counts = {}
        
        for target_id, voters in day_votes.items():
            if target_id in game['players'] and game['players'][target_id]['alive']:
                vote_counts[target_id] = len(voters)
        
        result['vote_counts'] = vote_counts
        
        # Execute most voted player (if there are votes)
        if vote_counts:
            max_votes = max(vote_counts.values())
            most_voted_players = [pid for pid, votes in vote_counts.items() if votes == max_votes]
            
            # In case of tie, random selection
            if most_voted_players:
                executed_id = random.choice(most_voted_players)
                game['players'][executed_id]['alive'] = False
                result['executed'] = {
                    'player_id': executed_id,
                    'name': game['players'][executed_id]['name'],
                    'role': game['players'][executed_id]['role'],
                    'votes': vote_counts[executed_id]
                }
        
        # Clear day votes and player votes
        game_updates = {
            'actions': {
                'werewolf_votes': {},
                'seer_target': None,
                'day_votes': {}
            }
        }
        
        for player in game['players'].values():
            player['vote'] = None

        game_updates['players'] = game['players']
        
        self.state_manager.update_game_state(game_id, game_updates)
        
        return result
    
    def check_win_condition(self, game_id: str) -> Optional[str]:
        """
        Check if the game has ended and return the winner.
        Returns: 'villagers', 'werewolves', or None if game continues.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game or not game['started']:
            return None
        
        alive_players = [p for p in game['players'].values() if p['alive']]
        alive_werewolves = [p for p in alive_players if p['role'] == 'werewolf']
        alive_villagers = [p for p in alive_players if p['role'] != 'werewolf']
        
        # Werewolves win if they equal or outnumber villagers
        if len(alive_werewolves) >= len(alive_villagers):
            self.state_manager.update_game_state(game_id, {
                'ended': True,
                'winner': 'werewolves',
                'phase': 'ended'
            })
            return 'werewolves'
        
        # Villagers win if no werewolves left
        if len(alive_werewolves) == 0:
            self.state_manager.update_game_state(game_id, {
                'ended': True,
                'winner': 'villagers',
                'phase': 'ended'
            })
            return 'villagers'
        
        return None
    
    def get_player_role_info(self, game_id: str, player_id: str) -> Dict:
        """
        Get role-specific information for a player.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game or player_id not in game['players']:
            return {'error': 'Player not found'}
        
        player = game['players'][player_id]
        role = player['role']

        is_alive = player['alive']
        
        if role == 'werewolf':
            # Werewolf can see other werewolves
            other_werewolves = [
                {'id': pid, 'name': p['name']}
                for pid, p in game['players'].items()
                if p['role'] == 'werewolf' and pid != player_id and p['alive']
            ]
            return {
                'role': 'werewolf',
                'allies': other_werewolves,
                'can_kill': game['phase'] == 'night',
                'is_alive': is_alive
            }
        
        elif role == 'seer':
            # Seer can investigate one player per night
            # (This could be expanded to track previous investigations)
            seer_history = game.get('seer_history', [])
            return {
                'role': 'seer',
                'can_investigate': game['phase'] == 'night',
                'previous_investigations': seer_history,
                'is_alive': is_alive
            }
        
        else:  # villager
            return {
                'role': 'villager',
                'objective': 'Find and eliminate all werewolves',
                'is_alive': is_alive
            }
    
    def validate_action(self, game_id: str, player_id: str, action_type: str, target_id: str = None) -> Tuple[bool, str]:
        """
        Validate if a player can perform the specified action.
        Returns (is_valid, error_message).
        """
        game = self.state_manager.get_game_state(game_id)
        if not game:
            return False, "Game not found"
        
        if game['ended']:
            return False, "Game has ended"
        
        if not game['started']:
            return False, "Game hasn't started yet"
        
        if player_id not in game['players']:
            return False, "Player not found"
        
        player = game['players'][player_id]
        if not player['alive']:
            return False, "Dead players cannot act"
        
        if target_id and target_id not in game['players']:
            return False, "Target player not found"
        
        if target_id and not game['players'][target_id]['alive']:
            return False, "Cannot target dead player"
        
        current_phase = game['phase']
        
        if action_type == 'werewolf_vote':
            if player['role'] != 'werewolf':
                return False, "Only werewolves can perform werewolf votes"
            if current_phase != 'night':
                return False, "Werewolf votes only allowed during night phase"
            if target_id == player_id:
                return False, "Cannot target yourself"
        
        elif action_type == 'seer_investigate':
            if player['role'] != 'seer':
                return False, "Only seers can investigate"
            if current_phase != 'night':
                return False, "Investigations only allowed during night phase"
            if target_id == player_id:
                return False, "Cannot investigate yourself"
        
        elif action_type == 'day_vote':
            if current_phase != 'day':
                return False, "Voting only allowed during day phase"
            if target_id == player_id:
                return False, "Cannot vote for yourself"
        
        elif action_type == 'chat':
            if current_phase != 'day':
                return False, "Chat only allowed during day phase"
        
        else:
            return False, "Unknown action type"
        
        return True, ""
    
    def get_alive_players(self, game_id: str) -> List[Dict]:
        """Get list of alive players."""
        game = self.state_manager.get_game_state(game_id)
        if not game:
            return []
        
        return [
            {
                'id': pid,
                'name': player['name'],
                'alive': player['alive']
            }
            for pid, player in game['players'].items()
            if player['alive']
        ]
    
    def get_game_summary(self, game_id: str, player_id: str = None) -> Dict:
        """
        Get a summary of the game state, filtered for the requesting player.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game:
            return {'error': 'Game not found'}
        
        # Public information
        summary = {
            'game_id': game_id,
            'phase': game['phase'],
            'started': game['started'],
            'ended': game['ended'],
            'winner': game.get('winner'),
            'players': [],
            'alive_count': 0,
            'dead_count': 0
        }
        
        # Player information (role hidden unless game ended or it's the player themselves)
        for pid, player in game['players'].items():
            player_info = {
                'id': pid,
                'name': player['name'],
                'alive': player['alive']
            }
            
            # Show role if game ended or it's the requesting player
            if game['ended'] or pid == player_id:
                player_info['role'] = player['role']
            
            summary['players'].append(player_info)
            
            if player['alive']:
                summary['alive_count'] += 1
            else:
                summary['dead_count'] += 1
        
        # Add phase timing if available
        if game.get('phase_end'):
            summary['phase_end'] = game['phase_end']
            summary['time_remaining'] = max(0, game['phase_end'] - time.time()) if game['phase_end'] else None
        
        # Add recent chat (last 10 messages during day phase)
        if game['phase'] == 'day' and game['chat']:
            summary['recent_chat'] = game['chat'][-10:]
        
        return summary
    
