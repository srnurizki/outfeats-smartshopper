"use client"

export interface Product {
    name: string
    meta: string
    price: string
    imageUrl?: string
}

interface MessageBubbleProps {
    role: "user" | "assistant"
    text: string
    timestamp: string
    products?: Product[]
}

export default function MessageBubble({ role, text, timestamp, products }: MessageBubbleProps) {
    if (role === "user") {
        return (
            <div className="flex flex-col items-end gap-1">
                <div className="max-w-[65%] rounded-[20px] rounded-br-[5px] bg-[#373737] px-[18px] py-[13px] text-sm leading-relaxed text-white">
                    {text}
                </div>
                <span className="text-[11px] text-[#939393]">{timestamp}</span>
            </div>
        )
    }

    return (
        <div className="flex flex-col items-start gap-1">
            <div className="flex items-end gap-2.5">
                <div className="flex h-7 w-7 min-w-7 items-center justify-center rounded-full bg-[#373737]">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                        <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" />
                        <line x1="3" y1="6" x2="21" y2="6" />
                        <path d="M16 10a4 4 0 01-8 0" />
                    </svg>
                </div>
                <div className="flex flex-col gap-2.5">
                    <div className="max-w-[68%] min-w-fit rounded-[20px] rounded-bl-[5px] border-[0.5px] border-[#E8E8E8] bg-white px-[18px] py-[13px] text-sm leading-relaxed text-[#373737] whitespace-pre-wrap">
                        {text}
                    </div>
                    {products?.map((p, i) => (
                        <div key={i} className="max-w-[280px] overflow-hidden rounded-xl border-[0.5px] border-[#E8E8E8] bg-white">
                            <div className="px-[13px] py-[11px]">
                                <p className="mb-0.5 text-[11px] text-[#939393]">({i + 1})</p>
                                <p className="mb-1 text-[13px] font-medium text-[#373737]">{p.name}</p>
                                <p className="text-[11px] leading-relaxed text-[#939393]">{p.meta}</p>
                                <p className="mt-1 text-[13px] font-medium text-[#118AF4]">{p.price}</p>
                            </div>
                            {p.imageUrl && (
                                <img
                                    src={p.imageUrl}
                                    alt={p.name}
                                    className="h-[140px] w-full border-t-[0.5px] border-[#E8E8E8] object-cover"
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>
            <span className="ml-[38px] text-[11px] text-[#939393]">{timestamp}</span>
        </div>
    )
}