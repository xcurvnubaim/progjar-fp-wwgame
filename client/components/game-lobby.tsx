"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Play, Copy, Check } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

interface GameLobbyProps {
  gameState: any
  gameId: string
  playerId: string
  playerName: string
}

export function GameLobby({ gameState, gameId, playerId, playerName }: GameLobbyProps) {
  const [isStarting, setIsStarting] = useState(false)
  const [copied, setCopied] = useState(false)

  const startGame = async () => {
    setIsStarting(true)
    try {
      await fetch(`${API_BASE}/games/${gameId}/start`, {
        method: "POST",
      })
    } catch (error) {
      console.error("Failed to start game:", error)
    }
    setIsStarting(false)
  }

  const copyGameId = () => {
    navigator.clipboard.writeText(gameId)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const canStart = gameState?.players?.length >= 3

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
        <CardHeader>
          <CardTitle className="text-white flex items-center justify-between">
            <div className="flex items-center">
              <Users className="h-6 w-6 mr-2 text-purple-400" />
              Game Lobby
            </div>
            <Badge variant="secondary" className="bg-purple-600 text-white">
              {gameState?.players?.length || 0} Players
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
            <div>
              <p className="text-purple-200 text-sm">Game ID</p>
              <p className="text-white font-mono text-lg">{gameId}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={copyGameId}
              className="border-purple-500/20 text-purple-300 hover:bg-purple-600/20 bg-transparent"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">Players</h3>
            <div className="space-y-2">
              {gameState?.players?.map((player: any) => (
                <div
                  key={player.id}
                  className={`p-3 rounded-lg border transition-all duration-200 ${
                    player.id === playerId
                      ? "bg-purple-600/20 border-purple-500/40"
                      : "bg-slate-700/30 border-slate-600/30"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">{player.name}</span>
                    {player.id === playerId && (
                      <Badge variant="secondary" className="bg-purple-600 text-white text-xs">
                        You
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {!canStart && (
              <div className="p-4 bg-yellow-900/20 border border-yellow-500/20 rounded-lg">
                <p className="text-yellow-400 text-sm">Need at least 3 players to start the game</p>
              </div>
            )}

            <Button
              onClick={startGame}
              disabled={!canStart || isStarting}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-600"
            >
              <Play className="h-4 w-4 mr-2" />
              {isStarting ? "Starting Game..." : "Start Game"}
            </Button>
          </div>

          <div className="text-center">
            <p className="text-purple-200 text-sm">Share the Game ID with your friends to have them join!</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
