"use client"

import { useState, useEffect } from "react"
import { GameLobby } from "@/components/game-lobby"
import { GameBoard } from "@/components/game-board"
import { ConnectionStatus } from "@/components/connection-status"
import { useGameState } from "@/hooks/use-game-state"

export default function GamePage() {
  const [gameId, setGameId] = useState<string | null>(null)
  const [playerId, setPlayerId] = useState<string | null>(null)
  const [playerName, setPlayerName] = useState<string | null>(null)

  useEffect(() => {
    setGameId(localStorage.getItem("gameId"))
    setPlayerId(localStorage.getItem("playerId"))
    setPlayerName(localStorage.getItem("playerName"))
  }, [])

  const { gameState, playerInfo, loading, connectionStatus, lastFetch, error } = useGameState(gameId, playerId)

  if (!gameId || !playerId || !playerName) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-center">
          <h1 className="text-2xl font-bold mb-4">No Game Found</h1>
          <p className="text-purple-200">Please return to the home page and join a game.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p>Loading game...</p>
        </div>
      </div>
    )
  }

  const connectionProps = {
    status: connectionStatus,
    lastFetch,
    error,
  }

  if (!gameState?.started) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-4">
          <div className="mb-4">
            <ConnectionStatus {...connectionProps} />
          </div>
          <GameLobby gameState={gameState} gameId={gameId} playerId={playerId} playerName={playerName} />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-4">
        <div className="mb-4">
          <ConnectionStatus {...connectionProps} />
        </div>
        <GameBoard
          gameState={gameState}
          playerInfo={playerInfo}
          gameId={gameId}
          playerId={playerId}
          playerName={playerName}
        />
      </div>
    </div>
  )
}
