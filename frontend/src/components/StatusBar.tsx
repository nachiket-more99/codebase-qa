import { useEffect, useState } from "react"
import { API_BASE } from "@/config"

type Status = {
  total_files: number
  total_chunks: number
}

export default function StatusBar() {
  const [status, setStatus] = useState<Status | null>(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_BASE}/status`)
        const data = await res.json()
        setStatus(data)
      } catch {
        setStatus(null)
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2">
      <span
        className="inline-block w-2 h-2 rounded-full"
        style={{
          background: status ? "#00e5a0" : "#ef4444",
          boxShadow: status ? "0 0 6px #00e5a0" : "none",
        }}
      />
      {status ? (
        <span style={{ fontSize: 11, color: "#64748b", fontFamily: "JetBrains Mono" }}>
          <span style={{ color: "#00e5a0" }}>{status.total_files}</span> files ·{" "}
          <span style={{ color: "#00e5a0" }}>{status.total_chunks}</span> chunks
        </span>
      ) : (
        <span style={{ fontSize: 11, color: "#ef4444", fontFamily: "JetBrains Mono" }}>
          backend offline
        </span>
      )}
    </div>
  )
}