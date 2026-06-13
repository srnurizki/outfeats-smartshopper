"use client"

import { useState } from "react"

interface ChatInputProps {
    onSend: (message: string) => void
    disabled: boolean
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [input, setInput] = useState("")

    function handleSend() {
        if (!input.trim() || disabled) return
        onSend(input.trim())
        setInput("")
    }

    function handleKeyDown(e: React.KeyboardEvent) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="rounded-2xl border-[1.5px] border-[#B8D4F8] bg-white px-4 py-3.5 flex flex-col gap-3">
            <textarea
                rows={2}
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                className="w-full resize-none border-none bg-transparent text-sm text-[#939393] placeholder-[#939393] outline-none focus:text-[#373737]"
            />
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 rounded-full border-[0.5px] border-[#B8D4F8] bg-[#EFF6FF] px-3 py-1">
                    <svg width="13" height="13" viewBox="0 0 14 14" fill="none" aria-hidden="true">
                        <path d="M7 0L8.5 5.5L14 7L8.5 8.5L7 14L5.5 8.5L0 7L5.5 5.5L7 0Z" fill="#118AF4" />
                    </svg>
                    <span className="text-xs font-medium text-[#373737]">Outfeats AI 1.0</span>
                </div>
                <button
                    onClick={handleSend}
                    disabled={disabled}
                    aria-label="Send"
                    className="flex h-[34px] w-[34px] items-center justify-center rounded-full bg-[#118AF4] text-white disabled:opacity-50"
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <line x1="12" y1="19" x2="12" y2="5" />
                        <polyline points="5 12 12 5 19 12" />
                    </svg>
                </button>
            </div>
        </div>
    )
}