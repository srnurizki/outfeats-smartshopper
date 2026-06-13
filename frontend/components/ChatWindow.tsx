"use client"

import { useEffect, useRef } from "react"
import MessageBubble, { Product } from "./MessageBubble"

export interface Message {
    role: "user" | "assistant"
    text: string
    timestamp: string
    products?: Product[]
}

interface ChatWindowProps {
    messages: Message[]
    loading: boolean
}

export default function ChatWindow({ messages, loading }: ChatWindowProps) {
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, loading])

    return (
        <div className="flex flex-1 flex-col gap-5 overflow-y-auto px-7 py-5">
            {messages.map((m, i) => (
                <MessageBubble key={i} role={m.role} text={m.text} timestamp={m.timestamp} products={m.products} />
            ))}
            {loading && (
                <div className="flex items-end gap-2.5">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#373737]">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                            <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" />
                        </svg>
                    </div>
                    <div className="flex gap-1.5 rounded-[20px] rounded-bl-[5px] border-[0.5px] border-[#E8E8E8] bg-white px-4 py-3.5">
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#939393]" />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#939393] [animation-delay:0.15s]" />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#939393] [animation-delay:0.3s]" />
                    </div>
                </div>
            )}
            <div ref={bottomRef} />
        </div>
    )
}