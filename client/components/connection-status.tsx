"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Wifi, WifiOff, Clock, ChevronUp, ChevronDown } from "lucide-react"

interface ConnectionStatusProps {
  status: "connected" | "disconnected" | "connecting"
  lastFetch: Date | null
  error?: string | null
}

export function ConnectionStatus({ status, lastFetch, error }: ConnectionStatusProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const getStatusColor = () => {
    switch (status) {
      case "connected":
        return "bg-green-600 text-white"
      case "disconnected":
        return "bg-red-600 text-white"
      case "connecting":
        return "bg-yellow-600 text-white"
      default:
        return "bg-gray-600 text-white"
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case "connected":
        return <Wifi className="h-4 w-4" />
      case "disconnected":
        return <WifiOff className="h-4 w-4" />
      case "connecting":
        return <Wifi className="h-4 w-4 animate-pulse" />
      default:
        return <WifiOff className="h-4 w-4" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case "connected":
        return "Connected"
      case "disconnected":
        return "Disconnected"
      case "connecting":
        return "Connecting..."
      default:
        return "Unknown"
    }
  }

  const formatLastFetch = () => {
    if (!lastFetch) return "Never"

    const now = new Date()
    const diff = Math.floor((now.getTime() - lastFetch.getTime()) / 1000)

    if (diff < 5) return "Just now"
    if (diff < 60) return `${diff}s ago`
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    return lastFetch.toLocaleTimeString()
  }

  return (
    <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur transition-all duration-300">
      <CardContent className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className={getStatusColor()}>
              {getStatusIcon()}
              <span className="ml-1 text-xs">{getStatusText()}</span>
            </Badge>

            {!isCollapsed && (
              <div className="flex items-center gap-2 text-xs text-purple-200">
                <Clock className="h-3 w-3" />
                <span>Last update: {formatLastFetch()}</span>
              </div>
            )}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="h-6 w-6 p-0 text-purple-300 hover:text-white hover:bg-purple-600/20"
          >
            {isCollapsed ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />}
          </Button>
        </div>

        {!isCollapsed && error && (
          <div className="mt-2 p-2 bg-red-900/20 border border-red-500/20 rounded text-xs text-red-400">{error}</div>
        )}
      </CardContent>
    </Card>
  )
}
