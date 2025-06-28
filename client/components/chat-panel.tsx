"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageCircle, Send } from "lucide-react"

const API_BASE = "http://localhost:8888"

interface ChatPanelProps {
  gameState: any
  gameId: string
  playerId: string
  playerName: string
}

export function ChatPanel({ gameState, gameId, playerId, playerName }: ChatPanelProps) {
  const [message, setMessage] = useState("")
  const [isSending, setIsSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [gameState?.recent_chat])

  const sendMessage = async () => {
    if (!message.trim() || isSending) return

    setIsSending(true)
    try {
      await fetch(`${API_BASE}/games/${gameId}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          player_id: playerId,
          message: message.trim(),
        }),
      })
      setMessage("")
    } catch (error) {
      console.error("Failed to send message:", error)
    }
    setIsSending(false)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getPlayerName = (playerId: string) => {
    const player = gameState?.players?.find((p: any) => p.id === playerId)
    return player?.name || "Unknown"
  }

  return (
    <Card className="bg-slate-800/50 border-purple-500/20 backdrop-blur">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          <MessageCircle className="h-5 w-5 mr-2 text-purple-400" />
          Village Chat
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-64 overflow-y-auto space-y-2 p-2 bg-slate-900/30 rounded border border-slate-600/30">
          {gameState?.recent_chat?.map((chat: any, index: number) => (
            <div key={index} className="text-sm transition-all duration-200 hover:bg-slate-800/30 p-1 rounded">
              <span className="text-purple-300 font-medium">{getPlayerName(chat.player)}:</span>
              <span className="text-white ml-2">{chat.message}</span>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            maxLength={200}
            className="bg-slate-700 border-slate-600 text-white transition-all duration-200 focus:border-purple-500"
          />
          <Button
            onClick={sendMessage}
            disabled={!message.trim() || isSending}
            size="sm"
            className="bg-purple-600 hover:bg-purple-700 transition-all duration-200"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-purple-300">{message.length}/200 characters</p>
      </CardContent>
    </Card>
  )
}
