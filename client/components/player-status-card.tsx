"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Heart, Skull, User } from "lucide-react"

interface PlayerStatusCardProps {
  playerInfo: any
  playerName: string
}

export function PlayerStatusCard({ playerInfo, playerName }: PlayerStatusCardProps) {
  const isAlive = playerInfo?.is_alive !== false // Default to true if not specified

  return (
    <Card
      className={`backdrop-blur transition-all duration-300 ${
        isAlive ? "bg-slate-800/50 border-green-500/20" : "bg-red-900/30 border-red-500/40"
      }`}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${isAlive ? "bg-green-600/20" : "bg-red-600/20"}`}>
              {isAlive ? <Heart className="h-5 w-5 text-green-400" /> : <Skull className="h-5 w-5 text-red-400" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-purple-300" />
                <span className="text-white font-medium">{playerName}</span>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <Badge
                  variant="outline"
                  className={
                    isAlive
                      ? "border-green-500 text-green-400 bg-green-500/10"
                      : "border-red-500 text-red-400 bg-red-500/10"
                  }
                >
                  {isAlive ? "Alive" : "Eliminated"}
                </Badge>
                {playerInfo?.role && (
                  <Badge
                    variant="outline"
                    className={
                      playerInfo.role === "werewolf"
                        ? "border-red-500 text-red-400"
                        : playerInfo.role === "seer"
                          ? "border-blue-500 text-blue-400"
                          : "border-green-500 text-green-400"
                    }
                  >
                    {playerInfo.role}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {!isAlive && (
            <div className="text-right">
              <div className="text-red-400 text-sm font-medium">Spectating</div>
              <div className="text-red-300 text-xs">Game continues...</div>
            </div>
          )}
        </div>

        {!isAlive && (
          <div className="mt-3 p-3 bg-red-900/20 border border-red-500/20 rounded">
            <p className="text-red-300 text-sm">
              💀 You have been eliminated from the game. You can continue to watch but cannot vote or take actions.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
