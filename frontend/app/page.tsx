"use client"

import { useState } from "react"
import LiquidChrome from "@/components/LiquidChrome"
import ChatInput from "@/components/ChatInput"
import ChatWindow, { Message } from "@/components/ChatWindow"
import SuggestionCards from "@/components/SuggestionCards"
import { sendMessage } from "@/lib/api"

function now() {
    return new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })
}

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([])
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [landingInput, setLandingInput] = useState("")

    const isLanding = messages.length === 0

    async function handleSend(text: string) {
        setMessages((prev) => [...prev, { role: "user", text, timestamp: now() }])
        setLoading(true)
        try {
            const data = await sendMessage(text, sessionId)
            setSessionId(data.session_id)
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: data.response,
                    timestamp: now(),
                    products: data.products?.map((p: any) => ({
                    name: p.name,
                     meta: p.meta,
                    price: p.price,
                    imageUrl: p.image_url
                    }))
                }
            ])
        } catch {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    text: "Something went wrong. Please try again.",
                    timestamp: now()
                }
            ])
        } finally {
            setLoading(false)
        }
    }

    function handleNewChat() {
        setMessages([])
        setSessionId(null)
        setLandingInput("")
    }

    if (isLanding) {
        return (
            <main className="relative flex min-h-screen flex-col" style={{zIndex: 0}}>
                <LiquidChrome />
                <header className="flex items-center justify-between px-8 py-5">
                    <span className="text-sm text-white/60">Outfeats AI 1.0</span>
                    <button
                        onClick={handleNewChat}
                        className="flex items-center gap-1.5 rounded-[10px] bg-[#118AF4] px-4 py-2 text-[13px] font-medium text-white"
                    >
                        New chat
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                            <line x1="12" y1="8" x2="12" y2="12" />
                            <line x1="10" y1="10" x2="14" y2="10" />
                        </svg>
                    </button>
                </header>

                <div className="flex flex-1 flex-col items-center justify-center gap-7 px-6">
                    <div className="text-center">
                        <h1 className="mb-2 text-[28px] font-bold leading-snug text-white [text-shadow:0_2px_20px_rgba(0,0,0,0.12)]">
                            Hi! Got new outfit ideas to actualize?
                        </h1>
                        <p className="text-sm text-white/70">
                            Ask any fashion products, I&apos;ll help you find in the marketplace.
                        </p>
                    </div>

                    <div className="flex w-full max-w-[560px] items-center rounded-full border-[0.5px] border-[#B8D4F8]/60 bg-white/95 py-1.5 pl-5 pr-1.5">
                        <input
                            type="text"
                            placeholder="Pajama dress, floral pattern, orange color, cotton material"
                            value={landingInput}
                            onChange={(e) => setLandingInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && landingInput.trim()) {
                                    handleSend(landingInput.trim())
                                    setLandingInput("")
                                }
                            }}
                            className="flex-1 border-none bg-transparent text-sm text-[#939393] outline-none focus:text-[#373737]"
                        />
                        <button
                            onClick={() => {
                                if (landingInput.trim()) {
                                    handleSend(landingInput.trim())
                                    setLandingInput("")
                                }
                            }}
                            className="flex items-center gap-1.5 rounded-full bg-[#118AF4] px-5 py-2.5 text-[13px] font-medium text-white"
                        >
                            Ask
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                <line x1="22" y1="2" x2="11" y2="13" />
                                <polygon points="22 2 15 22 11 13 2 9 22 2" />
                            </svg>
                        </button>
                    </div>

                    <SuggestionCards onSelect={handleSend} />
                </div>

                <footer className="py-4 text-center text-[11px] text-white/35">
                    Outfeats AI © 2026 Ryo Nurizki
                </footer>
            </main>
        )
    }

    return (
        <main className="flex min-h-screen flex-col bg-[#F2F2F2]">
            <header className="relative flex items-center justify-between px-8 py-5">
                <span className="text-sm text-[#939393]">Outfeats AI 1.0</span>
                <span className="absolute left-1/2 -translate-x-1/2 text-sm font-medium text-[#373737]">
                    Product Search
                </span>
                <button
                    onClick={handleNewChat}
                    className="flex items-center gap-1.5 rounded-[10px] bg-[#118AF4] px-4 py-2 text-[13px] font-medium text-white"
                >
                    New chat
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="10" y1="10" x2="14" y2="10" />
                    </svg>
                </button>
            </header>

            <ChatWindow messages={messages} loading={loading} />

            <div className="px-7 pb-5 pt-2">
                <ChatInput onSend={handleSend} disabled={loading} />
            </div>
        </main>
    )
}