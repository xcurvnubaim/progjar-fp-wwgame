"use client"

import { useEffect, useState } from "react"
import { Progress } from "@/components/ui/progress"
import { Clock } from "lucide-react"

interface PhaseTimerProps {
  gameState: any
}

export function PhaseTimer({ gameState }: PhaseTimerProps) {
  const [timeRemaining, setTimeRemaining] = useState(gameState?.time_remaining || 0)

  useEffect(() => {
    if (!gameState?.phase_end) return

    const interval = setInterval(() => {
      const now = Date.now() / 1000
      const remaining = Math.max(0, gameState.phase_end - now)
      setTimeRemaining(remaining)
    }, 1000)

    return () => clearInterval(interval)
  }, [gameState?.phase_end])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  const totalTime = gameState?.phase === "night" ? 60 : 120 // Assuming 1 min night, 2 min day
  const progress = ((totalTime - timeRemaining) / totalTime) * 100

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center text-purple-200">
          <Clock className="h-4 w-4 mr-2" />
          <span className="text-sm">Time Remaining</span>
        </div>
        <span className="text-white font-mono text-lg">{formatTime(timeRemaining)}</span>
      </div>
      <Progress value={progress} className="h-2 bg-slate-700" />
    </div>
  )
}
