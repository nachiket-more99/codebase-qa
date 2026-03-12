import { API_BASE } from "@/config"

export const askQuestion = async (question: string, topK: number = 5) => {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed")
  return data
}