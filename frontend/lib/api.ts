export interface ProductItem {
    name: string
    price: string
    meta: string
    image_url?: string
}

interface ChatApiResponse {
    response: string
    session_id: string
    products?: ProductItem[]
}

const API_URL = process.env.NEXT_PUBLIC_API_URL

if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not defined")
}

export async function sendMessage(
    message: string,
    sessionId: string | null
): Promise<ChatApiResponse> {
    const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId })
    })

    if (!res.ok) throw new Error(`Request failed: ${res.status}`)

    const data: ChatApiResponse = await res.json()

    if (!data.response || !data.session_id) {
        throw new Error("Invalid response shape from server")
    }

    return data
}