import { API_BASE } from "@/config"

export const ingestRepo = async (repoUrl: string) => {
  const res = await fetch(`${API_BASE}/ingest-repo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed")
  return data
}

export const ingestSingleFile = async (file: File) => {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/ingest`, { method: "POST", body: form })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed")
  return data
}

export const ingestMultipleFiles = async (files: File[]) => {
  const form = new FormData()
  files.forEach((f) => form.append("files", f))
  const res = await fetch(`${API_BASE}/ingest-multiple`, { method: "POST", body: form })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed")
  return data
}

export const clearIndex = async () => {
  const res = await fetch(`${API_BASE}/clear`, { method: "DELETE" })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || "Failed")
  return data
}