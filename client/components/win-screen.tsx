"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, Home } from "lucide-react"

interface WinScreenProps {
  gameState: any
  playerInfo: any
}

export function WinScreen({ gameState, playerInfo }: WinScreenProps) {
  const winner = gameState?.winner
  const playerWon =
    (winner === "werewolves" && playerInfo?.role === "werewolf") ||
    (winner === "villagers" && playerInfo?.role !== "werewolf")

  const goHome = () => {
    localStorage.removeItem("gameId")
    localStorage.removeItem("playerId")
    localStorage.removeItem("playerName")
    window.location.href = "/"
  }

  return (
    <div className="flex items-center justify-center min-h-[80vh]">
      <Card className="max-w-2xl mx-auto bg-slate-800/50 border-purple-500/20 backdrop-blur">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Trophy className={`h-16 w-16 ${playerWon ? "text-yellow-400" : "text-gray-400"}`} />
          </div>
          <CardTitle className="text-3xl text-white mb-2">Game Over!</CardTitle>
          <div className="space-y-2">
            <Badge
              variant="secondary"
              className={`text-lg px-4 py-2 ${
                winner === "werewolves" ? "bg-red-600 text-white" : "bg-green-600 text-white"
              }`}
            >
              {winner === "werewolves" ? "Werewolves Win!" : "Villagers Win!"}
            </Badge>
            <div>
              <Badge
                variant="outline"
                className={`${playerWon ? "border-green-500 text-green-400" : "border-red-500 text-red-400"}`}
              >
                You {playerWon ? "Won" : "Lost"}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <p className="text-purple-200 mb-4">
              {winner === "werewolves"
                ? "The werewolves have eliminated enough villagers to take control of the village!"
                : "The villagers successfully identified and eliminated all the werewolves!"}
            </p>
            <p className="text-purple-300 text-sm">
              Your role: <span className="font-semibold">{playerInfo?.role}</span>
            </p>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-3">Final Player Roles:</h3>
            <div className="space-y-2">
              {gameState?.players?.map((player: any) => (
                <div
                  key={player.id}
                  className={`p-3 rounded border transition-all duration-200 ${
                    player.alive ? "bg-green-900/20 border-green-500/20" : "bg-red-900/20 border-red-500/20"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-white">{player.name}</span>
                    <div className="flex gap-2">
                      <Badge
                        variant="outline"
                        className={
                          player.role === "werewolf"
                            ? "border-red-500 text-red-400"
                            : player.role === "seer"
                              ? "border-blue-500 text-blue-400"
                              : "border-green-500 text-green-400"
                        }
                      >
                        {player.role}
                      </Badge>
                      <Badge variant={player.alive ? "default" : "destructive"} className="text-xs">
                        {player.alive ? "Alive" : "Dead"}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-center">
            <Button onClick={goHome} className="bg-purple-600 hover:bg-purple-700">
              <Home className="h-4 w-4 mr-2" />
              Return Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
