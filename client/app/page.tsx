"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Moon, Users, Zap } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

export default function HomePage() {
  const [gameId, setGameId] = useState("")
  const [playerName, setPlayerName] = useState("")
  const [isCreating, setIsCreating] = useState(false)
  const [isJoining, setIsJoining] = useState(false)

  const createGame = async () => {
    setIsCreating(true)
    try {
      const response = await fetch(`${API_BASE}/games`, {
        method: "POST",
      })
      if (!response.ok) {
        alert(response.statusText)
        setIsCreating(false)
        return
      }
      const data = await response.json()
      if (response.ok) {
        setGameId(data.game_id)
      }
    } catch (error) {
      console.error("Failed to create game:", error)
    }
    setIsCreating(false)
  }

  const joinGame = async () => {
    if (!gameId || !playerName) return

    setIsJoining(true)
    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/join`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: playerName }),
      })
      const data = await response.json()
      if (response.ok) {
        // Store player info and redirect to game
        localStorage.setItem("gameId", gameId)
        localStorage.setItem("playerId", data.player_id)
        localStorage.setItem("playerName", playerName)
        window.location.href = "/game"
      }
    } catch (error) {
      console.error("Failed to join game:", error)
    }
    setIsJoining(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center mb-6">
            <Moon className="h-16 w-16 text-purple-400 mr-4" />
            <h1 className="text-6xl font-bold text-white">Werewolf</h1>
          </div>
          <p className="text-xl text-purple-200 max-w-2xl mx-auto">
            A thrilling multiplayer game of deception, strategy, and survival. Will you hunt the werewolves or become
            their prey?
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Zap className="h-5 w-5 mr-2 text-yellow-400" />
                Create New Game
              </CardTitle>
              <CardDescription className="text-purple-200">
                Start a new Werewolf game and invite your friends
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button onClick={createGame} disabled={isCreating} className="w-full bg-purple-600 hover:bg-purple-700">
                {isCreating ? "Creating..." : "Create Game"}
              </Button>
              {gameId && (
                <div className="p-4 bg-green-900/20 border border-green-500/20 rounded-lg">
                  <p className="text-green-400 font-mono text-sm">
                    Game ID: <span className="font-bold">{gameId}</span>
                  </p>
                  <p className="text-green-300 text-xs mt-1">Share this ID with your friends!</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Users className="h-5 w-5 mr-2 text-blue-400" />
                Join Existing Game
              </CardTitle>
              <CardDescription className="text-purple-200">Enter a game ID to join an existing game</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Game ID"
                value={gameId}
                onChange={(e) => setGameId(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white"
              />
              <Input
                placeholder="Your Name"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white"
              />
              <Button
                onClick={joinGame}
                disabled={isJoining || !gameId || !playerName}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {isJoining ? "Joining..." : "Join Game"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-white mb-8">How to Play</h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-slate-800/30 p-6 rounded-lg border border-purple-500/20">
              <div className="text-4xl mb-4">🌙</div>
              <h3 className="text-xl font-semibold text-white mb-2">Night Phase</h3>
              <p className="text-purple-200 text-sm">
                Werewolves secretly choose their victim while the Seer investigates a player
              </p>
            </div>
            <div className="bg-slate-800/30 p-6 rounded-lg border border-purple-500/20">
              <div className="text-4xl mb-4">☀️</div>
              <h3 className="text-xl font-semibold text-white mb-2">Day Phase</h3>
              <p className="text-purple-200 text-sm">
                All players discuss and vote to eliminate someone they suspect is a werewolf
              </p>
            </div>
            <div className="bg-slate-800/30 p-6 rounded-lg border border-purple-500/20">
              <div className="text-4xl mb-4">🏆</div>
              <h3 className="text-xl font-semibold text-white mb-2">Win Condition</h3>
              <p className="text-purple-200 text-sm">
                Villagers win by eliminating all werewolves. Werewolves win by equaling villagers
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
