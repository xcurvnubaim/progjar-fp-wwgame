"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Skull, Eye } from "lucide-react"

interface PlayerListProps {
  gameState: any
  playerId: string
}

export function PlayerList({ gameState, playerId }: PlayerListProps) {
  const alivePlayers = gameState?.players?.filter((p: any) => p.alive) || []
  const deadPlayers = gameState?.players?.filter((p: any) => !p.alive) || []

  return (
    <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <Users className="h-5 w-5 mr-2 text-purple-400" />
          Players
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-green-400 font-medium mb-2 flex items-center">Alive ({alivePlayers.length})</h4>
          <div className="space-y-2">
            {alivePlayers.map((player: any) => (
              <div
                key={player.id}
                className={`p-2 rounded border transition-all duration-200 ${
                  player.id === playerId
                    ? "bg-purple-600/20 border-purple-500/40"
                    : "bg-slate-700/30 border-slate-600/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-white text-sm">{player.name}</span>
                  <div className="flex items-center gap-1">
                    {player.id === playerId && (
                      <Badge variant="secondary" className="bg-purple-600 text-white text-xs">
                        You
                      </Badge>
                    )}
                    {/* Show if player has been investigated (for seers) */}
                    {player.investigated && (
                      <Eye className="h-3 w-3 text-blue-400" />
                    )}
                  </div>
                </div>
                {gameState?.ended && player.role && (
                  <Badge
                    variant="outline"
                    className={`text-xs mt-1 ${
                      player.role === "werewolf"
                        ? "border-red-500 text-red-400"
                        : player.role === "seer"
                          ? "border-blue-500 text-blue-400"
                          : "border-green-500 text-green-400"
                    }`}
                  >
                    {player.role}
                  </Badge>
                )}
              </div>
            ))}
          </div>
        </div>

        {deadPlayers.length > 0 && (
          <div>
            <h4 className="text-red-400 font-medium mb-2 flex items-center">
              <Skull className="h-4 w-4 mr-1" />
              Eliminated ({deadPlayers.length})
            </h4>
            <div className="space-y-2">
              {deadPlayers.map((player: any) => (
                <div key={player.id} className="p-2 rounded border bg-slate-700/20 border-slate-600/20 opacity-60">
                  <span className="text-gray-400 text-sm line-through">{player.name}</span>
                  {gameState?.ended && player.role && (
                    <Badge
                      variant="outline"
                      className={`text-xs mt-1 ml-2 ${
                        player.role === "werewolf"
                          ? "border-red-500 text-red-400"
                          : player.role === "seer"
                            ? "border-blue-500 text-blue-400"
                            : "border-green-500 text-green-400"
                      }`}
                    >
                      {player.role}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}