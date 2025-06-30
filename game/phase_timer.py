import threading
import time
from typing import Dict, Optional
from game.game_state import GameStateManager
from game.game_logic import GameLogic

# Phase durations in seconds
PHASE_DURATIONS = {
    'night': 20,  # 2 minutes
    'day': 20     # 5 minutes
}

class PhaseTimer:
    """
    Manages background timers for game phases.
    Handles automatic phase transitions and cleanup.
    """
    
    def __init__(self):
        self.state_manager = GameStateManager()
        self.game_logic = GameLogic()
        self.active_timers: Dict[str, threading.Timer] = {}
        self.timer_lock = threading.Lock()
    
    def start_phase_timer(self, game_id: str, phase: str) -> bool:
        """
        Start a timer for the specified phase.
        Sets phase_end timestamp and schedules automatic phase transition.
        """
        if phase not in PHASE_DURATIONS:
            return False
        
        game = self.state_manager.get_game_state(game_id)
        if not game or game['ended']:
            return False
        
        duration = PHASE_DURATIONS[phase]
        phase_end_time = time.time() + duration
        
        # Update game state with new phase and end time
        self.state_manager.update_game_state(game_id, {
            'phase': phase,
            'phase_end': phase_end_time
        })
        
        # Cancel any existing timer for this game
        self.cancel_timer(game_id)
        
        # Create and start new timer
        with self.timer_lock:
            timer = threading.Timer(duration, self._timer_callback, args=[game_id, phase])
            timer.daemon = True  # Timer won't prevent program exit
            timer.start()
            self.active_timers[game_id] = timer
        
        print(f"Started {phase} phase timer for game {game_id} ({duration}s)")
        return True
    
    def cancel_timer(self, game_id: str) -> bool:
        """Cancel the active timer for a game."""
        with self.timer_lock:
            if game_id in self.active_timers:
                self.active_timers[game_id].cancel()
                del self.active_timers[game_id]
                return True
        return False
    
    def _timer_callback(self, game_id: str, phase: str):
        """
        Called when a phase timer expires.
        Handles phase transition logic.
        """
        try:
            print(f"Phase timer expired for game {game_id}, phase: {phase}")
            
            # Remove timer from active list
            with self.timer_lock:
                if game_id in self.active_timers:
                    del self.active_timers[game_id]
            
            # Process phase end
            self.end_phase(game_id, phase)
            
        except Exception as e:
            print(f"Error in timer callback for game {game_id}: {e}")
    
    def end_phase(self, game_id: str, phase: str):
        """
        End the current phase and transition to the next phase.
        """
        game = self.state_manager.get_game_state(game_id)
        if not game or game['ended']:
            return
        
        print(f"Ending {phase} phase for game {game_id}")
        
        if phase == 'night':
            # Process night actions
            night_result = self.game_logic.resolve_night_actions(game_id)
            print(f"Night actions resolved for game {game_id}: {night_result}")
            
            # Check win condition
            winner = self.game_logic.check_win_condition(game_id)
            if winner:
                print(f"Game {game_id} ended, winner: {winner}")
                self.state_manager.update_game_state(game_id, {
                    'phase': 'ended',
                    'phase_end': None
                })
                return
            
            # Start day phase
            self.start_day_phase(game_id)
            
        elif phase == 'day':
            # Process day votes
            day_result = self.game_logic.resolve_day_votes(game_id)
            print(f"Day votes resolved for game {game_id}: {day_result}")
            
            # Check win condition
            winner = self.game_logic.check_win_condition(game_id)
            if winner:
                print(f"Game {game_id} ended, winner: {winner}")
                self.state_manager.update_game_state(game_id, {
                    'phase': 'ended',
                    'phase_end': None
                })
                return
            
            # Start night phase
            self.start_night_phase(game_id)
    
    def start_night_phase(self, game_id: str) -> bool:
        """Start the night phase for a game."""
        return self.start_phase_timer(game_id, 'night')
    
    def start_day_phase(self, game_id: str) -> bool:
        """Start the day phase for a game."""
        return self.start_phase_timer(game_id, 'day')
    
    def get_phase_time_remaining(self, game_id: str) -> Optional[float]:
        """Get the time remaining in the current phase."""
        game = self.state_manager.get_game_state(game_id)
        if not game or not game.get('phase_end'):
            return None
        
        remaining = game['phase_end'] - time.time()
        return max(0, remaining)
    
    def force_end_phase(self, game_id: str) -> bool:
        """
        Manually end the current phase (admin function).
        """
        game = self.state_manager.get_game_state(game_id)
        if not game or game['ended']:
            return False
        
        current_phase = game['phase']
        
        # Cancel the timer
        self.cancel_timer(game_id)
        
        # End the phase
        self.end_phase(game_id, current_phase)
        
        return True
    
    def get_active_timers(self) -> Dict[str, Dict]:
        """Get information about all active timers (for debugging)."""
        with self.timer_lock:
            active_info = {}
            for game_id, timer in self.active_timers.items():
                game = self.state_manager.get_game_state(game_id)
                if game:
                    remaining = self.get_phase_time_remaining(game_id)
                    active_info[game_id] = {
                        'phase': game['phase'],
                        'time_remaining': remaining,
                        'timer_active': timer.is_alive()
                    }
            return active_info
    
    def restore_timers_from_state(self):
        """
        Restore active timers from game state on server restart.
        This should be called during application initialization.
        """
        current_time = time.time()
        restored_count = 0
        
        # Get all games from state manager
        all_games = self.state_manager.get_all_games()
        
        for game_id, game in all_games.items():
            # Skip ended games or games without active phases
            if game.get('ended') or not game.get('started'):
                continue
                
            phase = game.get('phase')
            phase_end = game.get('phase_end')
            
            # Skip if no active phase or phase_end timestamp
            if not phase or not phase_end or phase in ['setup', 'ended']:
                continue
            
            # Calculate remaining time
            remaining_time = phase_end - current_time
            
            # If timer has already expired, process the phase end immediately
            if remaining_time <= 0:
                print(f"Timer for game {game_id} phase {phase} has expired, processing immediately")
                self.end_phase(game_id, phase)
                continue
            
            # If timer is still valid, restore it
            if phase in PHASE_DURATIONS:
                print(f"Restoring timer for game {game_id}, phase {phase}, {remaining_time:.1f}s remaining")
                
                # Cancel any existing timer for this game (shouldn't be any, but safety first)
                self.cancel_timer(game_id)
                
                # Create and start timer with remaining time
                with self.timer_lock:
                    timer = threading.Timer(remaining_time, self._timer_callback, args=[game_id, phase])
                    timer.daemon = True
                    timer.start()
                    self.active_timers[game_id] = timer
                
                restored_count += 1
        
        if restored_count > 0:
            print(f"Successfully restored {restored_count} active timers from game state")
        else:
            print("No active timers to restore")
        
        return restored_count

    def cleanup_finished_games(self):
        """Remove timers for ended games."""
        games_to_cleanup = []
        
        with self.timer_lock:
            for game_id in list(self.active_timers.keys()):
                game = self.state_manager.get_game_state(game_id)
                if not game or game['ended']:
                    games_to_cleanup.append(game_id)
        
        for game_id in games_to_cleanup:
            self.cancel_timer(game_id)
            print(f"Cleaned up timer for ended game {game_id}")


# Global instance for use across the application
phase_timer = PhaseTimer()
