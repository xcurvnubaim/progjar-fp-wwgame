"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PhaseTimer } from "@/components/phase-timer"
import { PlayerList } from "@/components/player-list"
import { ChatPanel } from "@/components/chat-panel"
import { ActionPanel } from "@/components/action-panel"
import { WinScreen } from "@/components/win-screen"
import { NightPhaseInfo } from "@/components/night-phase-info"
import { PlayerStatusCard } from "@/components/player-status-card"
import { Moon, Sun, Crown } from "lucide-react"

interface GameBoardProps {
  gameState: any
  playerInfo: any
  gameId: string
  playerId: string
  playerName: string
}

export function GameBoard({ gameState, playerInfo, gameId, playerId, playerName }: GameBoardProps) {
  if (gameState?.ended) {
    return <WinScreen gameState={gameState} playerInfo={playerInfo} />
  }

  const isNight = gameState?.phase === "night"
  const isDay = gameState?.phase === "day"
  const isPlayerAlive = playerInfo?.is_alive !== false // Default to true if not specified

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Main Game Area */}
      <div className="lg:col-span-2 space-y-6">
        {/* Player Status Card */}
        <PlayerStatusCard playerInfo={playerInfo} playerName={playerName} />

        {/* Phase Header */}
        <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <div className="flex items-center">
                {isNight ? (
                  <Moon className="h-6 w-6 mr-2 text-blue-400" />
                ) : (
                  <Sun className="h-6 w-6 mr-2 text-yellow-400" />
                )}
                {isNight ? "Night Phase" : "Day Phase"}
              </div>
              <Badge variant="secondary" className={isNight ? "bg-blue-600 text-white" : "bg-yellow-600 text-white"}>
                {gameState?.alive_count} Alive
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <PhaseTimer gameState={gameState} />
            <div className="mt-4">
              {isNight ? (
                <p className="text-purple-200">The village sleeps while dark forces move in the shadows...</p>
              ) : (
                <p className="text-purple-200">The village awakens to discuss and vote on who to eliminate.</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Night Phase Info for Werewolves */}
        {isNight && playerInfo?.role === "werewolf" && isPlayerAlive && (
          <NightPhaseInfo playerInfo={playerInfo} gameState={gameState} />
        )}

        {/* Player Role Info */}
        {playerInfo && (
          <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Crown className="h-5 w-5 mr-2 text-yellow-400" />
                Your Role: {playerInfo.role}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {playerInfo.role === "werewolf" && (
                <div>
                  <p className="text-red-300 mb-2">
                    You are a werewolf! Work with your pack to eliminate the villagers.
                  </p>
                  {playerInfo.allies && playerInfo.allies.length > 0 && (
                    <div>
                      <p className="text-purple-200 text-sm mb-1">Your allies:</p>
                      <div className="flex gap-2">
                        {playerInfo.allies.map((ally: any) => (
                          <Badge key={ally.id} variant="destructive">
                            {ally.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {playerInfo.role === "seer" && (
                <div>
                  <p className="text-blue-300 mb-2">
                    You are the seer! Use your power to investigate players and find the werewolves.
                  </p>
                  <p className="text-blue-200 text-sm">
                    Your investigation results will be shown in the actions panel and persist throughout the game.
                  </p>
                </div>
              )}
              {playerInfo.role === "villager" && (
                <div>
                  <p className="text-green-300 mb-2">
                    You are a villager! Work with others to find and eliminate the werewolves.
                  </p>
                  {playerInfo.objective && <p className="text-green-200 text-sm">Objective: {playerInfo.objective}</p>}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Action Panel - Only show if player is alive */}
        {isPlayerAlive ? (
          <ActionPanel gameState={gameState} playerInfo={playerInfo} gameId={gameId} playerId={playerId} />
        ) : (
          <Card className="bg-slate-800/50 border-red-500/20 backdrop-blur">
            <CardContent className="p-6 text-center">
              <div className="space-y-4">
                <div className="text-red-400">
                  <h3 className="text-lg font-semibold mb-2">You have been eliminated</h3>
                  <p className="text-red-300">
                    You can no longer participate in voting or actions, but you can watch the game continue.
                  </p>
                </div>

                {/* Show seer investigation results even when dead */}
                {playerInfo?.role === "seer" &&
                  playerInfo?.previous_investigations &&
                  playerInfo.previous_investigations.length > 0 && (
                    <div className="p-4 bg-blue-900/20 border border-blue-500/20 rounded-lg">
                      <h4 className="text-blue-400 font-medium mb-3">Your Investigation Results:</h4>
                      <div className="space-y-2">
                        {playerInfo.previous_investigations.map((investigation: any, index: number) => {
                          const targetPlayer = gameState?.players?.find((p: any) => p.id === investigation.target_id)
                          return (
                            <div key={index} className="flex items-center justify-between text-sm">
                              <span className="text-white">{targetPlayer?.name || "Unknown"}</span>
                              <Badge
                                variant="outline"
                                className={
                                  investigation.target_role === "werewolf"
                                    ? "border-red-500 text-red-400"
                                    : "border-green-500 text-green-400"
                                }
                              >
                                {investigation.target_role === "werewolf" ? "Werewolf" : "Innocent"}
                              </Badge>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Player List */}
        <PlayerList gameState={gameState} playerId={playerId} />

        {/* Chat Panel (Day Phase Only and if player is alive) */}
        {isDay && isPlayerAlive && (
          <ChatPanel gameState={gameState} gameId={gameId} playerId={playerId} playerName={playerName} />
        )}

        {/* Dead player spectator message */}
        {!isPlayerAlive && (
          <Card className="bg-slate-800/50 border-red-500/20 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-red-400">Spectator Mode</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-300 text-sm">
                You are now spectating the game. You can watch the remaining players but cannot participate in
                discussions or voting.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
