#!/usr/bin/env python3
"""
Shared Memory Management Utility for Werewolf Game Server

This utility helps manage the shared memory used by the multiprocess Werewolf game server.
"""

import sys
import json
import pickle
from multiprocessing import shared_memory
import argparse

SHARED_MEMORY_NAME = "werewolf_game_state"

def view_shared_memory():
    """View the contents of the shared memory."""
    try:
        shm = shared_memory.SharedMemory(name=SHARED_MEMORY_NAME)
        
        # Read size header
        data_size = int.from_bytes(shm.buf[:8], byteorder='little')
        print(f"Shared memory size: {len(shm.buf)} bytes")
        print(f"Data size: {data_size} bytes")
        
        if data_size == 0:
            print("No data in shared memory")
            shm.close()
            return
        
        # Read and deserialize data
        serialized_data = bytes(shm.buf[8:8 + data_size])
        data = pickle.loads(serialized_data)
        
        print("\nShared memory contents:")
        print(json.dumps(data, indent=2, default=str))
        
        shm.close()
        
    except FileNotFoundError:
        print("Shared memory not found. Server may not be running.")
    except Exception as e:
        print(f"Error reading shared memory: {e}")

def cleanup_shared_memory():
    """Clean up (remove) the shared memory."""
    try:
        shm = shared_memory.SharedMemory(name=SHARED_MEMORY_NAME)
        shm.close()
        shm.unlink()
        print("Shared memory cleaned up successfully")
    except FileNotFoundError:
        print("Shared memory not found (already cleaned up)")
    except Exception as e:
        print(f"Error cleaning up shared memory: {e}")

def shared_memory_info():
    """Get information about the shared memory."""
    try:
        shm = shared_memory.SharedMemory(name=SHARED_MEMORY_NAME)
        
        data_size = int.from_bytes(shm.buf[:8], byteorder='little')
        
        print(f"Shared Memory Information:")
        print(f"  Name: {SHARED_MEMORY_NAME}")
        print(f"  Total size: {len(shm.buf)} bytes ({len(shm.buf) / 1024 / 1024:.2f} MB)")
        print(f"  Data size: {data_size} bytes ({data_size / 1024:.2f} KB)")
        print(f"  Used: {((data_size + 8) / len(shm.buf) * 100):.2f}%")
        print(f"  Available: {len(shm.buf) - data_size - 8} bytes")
        
        if data_size > 0:
            serialized_data = bytes(shm.buf[8:8 + data_size])
            data = pickle.loads(serialized_data)
            
            if isinstance(data, dict):
                print(f"  Games stored: {len(data)}")
                for game_id, game in data.items():
                    players = len(game.get('players', {}))
                    phase = game.get('phase', 'unknown')
                    print(f"    {game_id}: {players} players, phase: {phase}")
        
        shm.close()
        
    except FileNotFoundError:
        print("Shared memory not found. Server may not be running.")
    except Exception as e:
        print(f"Error getting shared memory info: {e}")

def monitor_shared_memory():
    """Monitor shared memory for changes."""
    import time
    
    print("Monitoring shared memory for changes (Ctrl+C to stop)...")
    last_data = None
    
    try:
        while True:
            try:
                shm = shared_memory.SharedMemory(name=SHARED_MEMORY_NAME)
                data_size = int.from_bytes(shm.buf[:8], byteorder='little')
                
                if data_size > 0:
                    serialized_data = bytes(shm.buf[8:8 + data_size])
                    current_data = pickle.loads(serialized_data)
                    
                    if current_data != last_data:
                        print(f"\n[{time.strftime('%H:%M:%S')}] Shared memory updated:")
                        if isinstance(current_data, dict):
                            for game_id, game in current_data.items():
                                players = len(game.get('players', {}))
                                phase = game.get('phase', 'unknown')
                                print(f"  Game {game_id}: {players} players, phase: {phase}")
                        last_data = current_data.copy() if isinstance(current_data, dict) else current_data
                
                shm.close()
                time.sleep(1)
                
            except FileNotFoundError:
                print("Shared memory not found. Waiting for server to start...")
                time.sleep(5)
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error monitoring: {e}")
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def main():
    parser = argparse.ArgumentParser(description="Manage Werewolf Game Server shared memory")
    parser.add_argument('action', choices=['view', 'cleanup', 'info', 'monitor'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'view':
        view_shared_memory()
    elif args.action == 'cleanup':
        cleanup_shared_memory()
    elif args.action == 'info':
        shared_memory_info()
    elif args.action == 'monitor':
        monitor_shared_memory()

if __name__ == '__main__':
    main()
