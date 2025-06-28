"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Target } from "lucide-react"

interface NightPhaseInfoProps {
  playerInfo: any
  gameState: any
}

export function NightPhaseInfo({ playerInfo, gameState }: NightPhaseInfoProps) {
  const getPlayerName = (playerId: string) => {
    const player = gameState?.players?.find((p: any) => p.id === playerId)
    return player?.name || "Unknown"
  }

  return (
    <Card className="bg-red-900/20 border-red-500/20 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-red-400 flex items-center">
          <Users className="h-5 w-5 mr-2" />
          Werewolf Pack Communication
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-red-300 text-sm mb-2">
            Coordinate with your pack to choose tonight's victim. You can see what other werewolves are targeting.
          </p>

          {playerInfo.allies && playerInfo.allies.length > 0 && (
            <div>
              <p className="text-red-200 text-sm mb-2">Your pack members:</p>
              <div className="flex gap-2 mb-3">
                {playerInfo.allies.map((ally: any) => (
                  <Badge key={ally.id} variant="destructive" className="bg-red-600">
                    {ally.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Show pack voting status if available */}
          {playerInfo.pack_votes && Object.keys(playerInfo.pack_votes).length > 0 && (
            <div className="p-3 bg-red-800/20 border border-red-600/20 rounded">
              <div className="flex items-center mb-2">
                <Target className="h-4 w-4 text-red-400 mr-2" />
                <span className="text-red-400 font-medium text-sm">Pack Voting Status:</span>
              </div>
              <div className="space-y-1">
                {Object.entries(playerInfo.pack_votes).map(([wolfId, targetId]) => (
                  <div key={wolfId} className="text-xs text-red-300">
                    <span className="font-medium">{getPlayerName(wolfId)}</span>
                    <span className="text-red-400 mx-1">→</span>
                    <span>{getPlayerName(targetId as string)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
