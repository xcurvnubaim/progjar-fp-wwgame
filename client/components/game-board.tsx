"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { PhaseTimer } from "@/components/phase-timer"
import { PlayerList } from "@/components/player-list"
import { ChatPanel } from "@/components/chat-panel"
import { ActionPanel } from "@/components/action-panel"
import { WinScreen } from "@/components/win-screen"
import { NightPhaseInfo } from "@/components/night-phase-info"
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

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Main Game Area */}
      <div className="lg:col-span-2 space-y-6">
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
        {isNight && playerInfo?.role === "werewolf" && <NightPhaseInfo playerInfo={playerInfo} gameState={gameState} />}

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
                <p className="text-green-300">
                  You are a villager! Work with others to find and eliminate the werewolves.
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Action Panel */}
        <ActionPanel gameState={gameState} playerInfo={playerInfo} gameId={gameId} playerId={playerId} />
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Player List */}
        <PlayerList gameState={gameState} playerId={playerId} />

        {/* Chat Panel (Day Phase Only) */}
        {isDay && <ChatPanel gameState={gameState} gameId={gameId} playerId={playerId} playerName={playerName} />}
      </div>
    </div>
  )
}
