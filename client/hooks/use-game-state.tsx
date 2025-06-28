"use client"

import { useState, useEffect, useCallback } from "react"

const API_BASE = "http://localhost:8888"

export function useGameState(gameId: string | null, playerId: string | null) {
  const [gameState, setGameState] = useState<any>(null)
  const [playerInfo, setPlayerInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState<"connected" | "disconnected" | "connecting">("connecting")
  const [lastFetch, setLastFetch] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)

  const fetchGameState = useCallback(async () => {
    if (!gameId) return

    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/state${playerId ? `?player_id=${playerId}` : ""}`)
      if (response.ok) {
        const data = await response.json()
        setGameState(data)
        setError(null)
        setConnectionStatus("connected")
        setLastFetch(new Date())
      } else {
        setError("Failed to fetch game state")
        setConnectionStatus("disconnected")
      }
    } catch (err) {
      setError("Network error")
      setConnectionStatus("disconnected")
    }
  }, [gameId, playerId])

  const fetchPlayerInfo = useCallback(async () => {
    if (!playerId || !gameId) return

    try {
      const response = await fetch(`${API_BASE}/games/${gameId}/player/${playerId}`)
      if (response.ok) {
        const data = await response.json()
        setPlayerInfo(data)
      }
    } catch (err) {
      console.error("Failed to fetch player info:", err)
    }
  }, [gameId, playerId])

  const fetchData = useCallback(async () => {
    setConnectionStatus("connecting")
    await Promise.all([fetchGameState(), fetchPlayerInfo()])
    setLoading(false)
  }, [fetchGameState, fetchPlayerInfo])

  useEffect(() => {
    if (!gameId) return

    fetchData()

    // Poll for updates every 2 seconds
    const interval = setInterval(fetchData, 2000)

    return () => clearInterval(interval)
  }, [gameId, playerId, fetchData])

  return {
    gameState,
    playerInfo,
    loading,
    connectionStatus,
    lastFetch,
    error,
  }
}
