"use client"

const SUGGESTIONS = [
    { title: "Find products", desc: "Browse fashion items", prompt: "Help me find fashion products" },
    { title: "Shipping info", desc: "Delivery and tracking", prompt: "Tell me about shipping options" },
    { title: "Returns", desc: "Refund and exchange", prompt: "How do I return an item?" },
    { title: "Support", desc: "General questions", prompt: "I need help with my order" }
]

const ICONS = [
    <path key="0" d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.57a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.57a2 2 0 0 0-1.34-2.23z" />,
    <g key="1"><rect x="1" y="3" width="15" height="13" /><polygon points="16 8 20 8 23 11 23 16 16 16 16 8" /><circle cx="5.5" cy="18.5" r="2.5" /><circle cx="18.5" cy="18.5" r="2.5" /></g>,
    <g key="2"><polyline points="17 1 21 5 17 9" /><path d="M3 11V9a4 4 0 0 1 4-4h14" /><polyline points="7 23 3 19 7 15" /><path d="M21 13v2a4 4 0 0 1-4 4H3" /></g>,
    <g key="3"><path d="M3 18v-6a9 9 0 0 1 18 0v6" /><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z" /></g>
]

interface SuggestionCardsProps {
    onSelect: (prompt: string) => void
}

export default function SuggestionCards({ onSelect }: SuggestionCardsProps) {
    return (
        <div className="grid w-full max-w-[680px] grid-cols-2 gap-3 md:grid-cols-4">
            {SUGGESTIONS.map((s, i) => (
                <button
                    key={s.title}
                    onClick={() => onSelect(s.prompt)}
                    className="flex flex-col gap-2.5 rounded-xl border-[0.5px] border-[#E8E8E8] bg-white p-4 text-left"
                >
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#373737" strokeWidth="1.5">
                        {ICONS[i]}
                    </svg>
                    <div>
                        <p className="text-[13px] font-medium text-[#373737]">{s.title}</p>
                        <p className="text-xs text-[#939393]">{s.desc}</p>
                    </div>
                </button>
            ))}
        </div>
    )
}