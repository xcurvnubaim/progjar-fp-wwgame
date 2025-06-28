"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Vote, Eye, Zap, CheckCircle } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE

interface ActionPanelProps {
  gameState: any
  playerInfo: any
  gameId: string
  playerId: string
}

export function ActionPanel({ gameState, playerInfo, gameId, playerId }: ActionPanelProps) {
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)
  const [isPerformingAction, setIsPerformingAction] = useState(false)
  const [actionCompleted, setActionCompleted] = useState<{
    type: string
    target: string
    result?: string
  } | null>(null)
  const [investigationResults, setInvestigationResults] = useState<{
    [playerId: string]: { name: string; role: string; timestamp: number }
  }>({})

  const isNight = gameState?.phase === "night"
  const isDay = gameState?.phase === "day"
  const isPlayerAlive = playerInfo?.is_alive !== false
  const alivePlayers = gameState?.players?.filter((p: any) => p.alive && p.id !== playerId) || []

  // Reset action completed when phase changes
  useEffect(() => {
    setActionCompleted(null)
    setSelectedTarget(null)
  }, [gameState?.phase])

  // Parse investigation results from API response
  useEffect(() => {
    if (playerInfo?.role === "seer" && playerInfo?.previous_investigations) {
      const results: { [key: string]: { name: string; role: string; timestamp: number } } = {}

      playerInfo.previous_investigations.forEach((investigation: any) => {
        const targetPlayer = gameState?.players?.find((p: any) => p.id === investigation.target_id)
        if (targetPlayer) {
          results[investigation.target_id] = {
            name: targetPlayer.name,
            role: investigation.target_role,
            timestamp: investigation.timestamp,
          }
        }
      })

      setInvestigationResults(results)
    }
  }, [playerInfo, gameState?.players])

  // Don't show action panel if player is dead
  if (!isPlayerAlive) {
    return null
  }

  const performAction = async (actionType: string) => {
    if (!selectedTarget || isPerformingAction) return

    const targetPlayer = alivePlayers.find((p: any) => p.id === selectedTarget)
    if (!targetPlayer) return

    setIsPerformingAction(true)
    try {
      const endpoint = actionType === "vote" ? "vote" : "action"
      const body =
        actionType === "vote"
          ? { player_id: playerId, target_id: selectedTarget }
          : { player_id: playerId, action_type: actionType, target_id: selectedTarget }

      const response = await fetch(`${API_BASE}/games/${gameId}/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      })

      if (response.ok) {
        // Set action completed with target info
        setActionCompleted({
          type: actionType,
          target: targetPlayer.name,
        })
      }

      setSelectedTarget(null)
    } catch (error) {
      console.error("Failed to perform action:", error)
    }
    setIsPerformingAction(false)
  }

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString()
  }

  const canPerformWerewolfAction = isNight && playerInfo?.role === "werewolf" && playerInfo?.can_kill
  const canPerformSeerAction = isNight && playerInfo?.role === "seer" && playerInfo?.can_investigate
  const canVote = isDay

  if (!canPerformWerewolfAction && !canPerformSeerAction && !canVote) {
    return (
      <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
        <CardContent className="p-6 space-y-4">
          <div className="text-center">
            <p className="text-purple-200">
              {isNight ? "Wait for others to complete their actions..." : "No actions available."}
            </p>
          </div>

          {/* Show seer investigation results */}
          {playerInfo?.role === "seer" && Object.keys(investigationResults).length > 0 && (
            <div className="p-4 bg-blue-900/20 border border-blue-500/20 rounded-lg">
              <h4 className="text-blue-400 font-medium mb-3 flex items-center">
                <Eye className="h-4 w-4 mr-2" />
                Your Investigation Results:
              </h4>
              <div className="space-y-3">
                {Object.entries(investigationResults)
                  .sort(([, a], [, b]) => b.timestamp - a.timestamp)
                  .map(([targetId, data]) => (
                    <div key={targetId} className="flex items-center justify-between p-2 bg-slate-800/30 rounded">
                      <div>
                        <span className="text-white font-medium">{data.name}</span>
                        <div className="text-xs text-blue-300">{formatTimestamp(data.timestamp)}</div>
                      </div>
                      <Badge
                        variant="outline"
                        className={
                          data.role === "werewolf" ? "border-red-500 text-red-400" : "border-green-500 text-green-400"
                        }
                      >
                        {data.role === "werewolf" ? "Werewolf" : "Innocent"}
                      </Badge>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <Zap className="h-5 w-5 mr-2 text-yellow-400" />
          Actions
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Show action completed message */}
        {actionCompleted && (
          <div className="p-4 bg-green-900/20 border border-green-500/20 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
              <div>
                <p className="text-green-400 font-medium">
                  {actionCompleted.type === "werewolf_vote" && `You voted to kill ${actionCompleted.target}`}
                  {actionCompleted.type === "seer_investigate" && `You investigated ${actionCompleted.target}`}
                  {actionCompleted.type === "vote" && `You voted to eliminate ${actionCompleted.target}`}
                </p>
                {actionCompleted.type === "seer_investigate" && (
                  <p className="text-blue-300 text-sm mt-1">The result will appear in your investigation history.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Show seer investigation results */}
        {playerInfo?.role === "seer" && Object.keys(investigationResults).length > 0 && (
          <div className="p-4 bg-blue-900/20 border border-blue-500/20 rounded-lg">
            <h4 className="text-blue-400 font-medium mb-3 flex items-center">
              <Eye className="h-4 w-4 mr-2" />
              Your Investigation Results:
            </h4>
            <div className="space-y-2">
              {Object.entries(investigationResults)
                .sort(([, a], [, b]) => b.timestamp - a.timestamp)
                .map(([targetId, data]) => (
                  <div key={targetId} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="text-white">{data.name}</span>
                      <div className="text-xs text-blue-300">{formatTimestamp(data.timestamp)}</div>
                    </div>
                    <Badge
                      variant="outline"
                      className={`ml-2 text-xs ${
                        investigationResults[targetId].role === "werewolf"
                          ? "border-red-500 text-red-400"
                          : "border-green-500 text-green-400"
                      }`}
                    >
                      {investigationResults[targetId].role === "werewolf" ? "WW" : "OK"}
                    </Badge>
                  </div>
                ))}
            </div>
          </div>
        )}

        {!actionCompleted && (
          <>
            {/* Target Selection */}
            <div>
              <h4 className="text-white font-medium mb-2">Select Target:</h4>
              <div className="grid grid-cols-2 gap-2">
                {alivePlayers.map((player: any) => (
                  <Button
                    key={player.id}
                    variant={selectedTarget === player.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedTarget(player.id)}
                    className={
                      selectedTarget === player.id
                        ? "bg-purple-600 hover:bg-purple-700 transition-all duration-200"
                        : "border-purple-500/20 text-purple-300 hover:bg-purple-600/20 transition-all duration-200"
                    }
                  >
                    {player.name}
                    {/* Show investigation result for seer */}
                    {playerInfo?.role === "seer" && investigationResults[player.id] && (
                      <Badge
                        variant="outline"
                        className={`ml-2 text-xs ${
                          investigationResults[player.id].role === "werewolf"
                            ? "border-red-500 text-red-400"
                            : "border-green-500 text-green-400"
                        }`}
                      >
                        {investigationResults[player.id].role === "werewolf" ? "WW" : "OK"}
                      </Badge>
                    )}
                  </Button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2">
              {canPerformWerewolfAction && (
                <Button
                  onClick={() => performAction("werewolf_vote")}
                  disabled={!selectedTarget || isPerformingAction}
                  className="w-full bg-red-600 hover:bg-red-700 transition-all duration-200"
                >
                  <Vote className="h-4 w-4 mr-2" />
                  {isPerformingAction ? "Voting..." : "Vote to Kill"}
                </Button>
              )}

              {canPerformSeerAction && (
                <Button
                  onClick={() => performAction("seer_investigate")}
                  disabled={!selectedTarget || isPerformingAction}
                  className="w-full bg-blue-600 hover:bg-blue-700 transition-all duration-200"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  {isPerformingAction ? "Investigating..." : "Investigate"}
                </Button>
              )}

              {canVote && (
                <Button
                  onClick={() => performAction("vote")}
                  disabled={!selectedTarget || isPerformingAction}
                  className="w-full bg-orange-600 hover:bg-orange-700 transition-all duration-200"
                >
                  <Vote className="h-4 w-4 mr-2" />
                  {isPerformingAction ? "Voting..." : "Vote to Eliminate"}
                </Button>
              )}
            </div>
          </>
        )}

        {/* Action Description */}
        <div className="p-3 bg-slate-700/30 rounded border border-slate-600/30">
          <p className="text-purple-200 text-sm">
            {canPerformWerewolfAction && "Vote with your pack to eliminate a villager."}
            {canPerformSeerAction && "Investigate a player to learn their role. Results will be shown above."}
            {canVote && "Vote to eliminate a player you suspect is a werewolf."}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
