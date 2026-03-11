import { useState } from "react"
import StatusBar from "@/components/StatusBar"

export default function App() {
  const [activeTab, setActiveTab] = useState<"ingest" | "chat">("ingest")

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "#0a0b0d" }}>

      {/* Header */}
      <header
        className="flex items-center justify-between px-6 py-3 border-b"
        style={{ borderColor: "#1e2430", background: "#0e1014" }}
      >
        <div className="flex items-center gap-2">
          <span style={{ color: "#00e5a0", fontFamily: "Syne", fontWeight: 800, fontSize: 16, letterSpacing: "0.08em" }}>
            [CODEBASE·QA]
          </span>
          <span
            className="inline-block w-2 h-4"
            style={{ background: "#00e5a0", animation: "blink 1.1s steps(1) infinite" }}
          />
        </div>
        <StatusBar />
      </header>

      {/* Tabs */}
      <nav
        className="flex px-6 border-b"
        style={{ borderColor: "#1e2430", background: "#0e1014" }}
      >
        {(["ingest", "chat"] as const).map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className="py-3 px-4 text-xs font-semibold tracking-widest transition-colors border-b-2"
            style={{
              fontFamily: "JetBrains Mono",
              borderBottomColor: activeTab === tab ? "#00e5a0" : "transparent",
              color: activeTab === tab ? "#00e5a0" : "#64748b",
            }}
          >
            <span style={{ color: "#334155", marginRight: 6 }}>0{i + 1}</span>
            {tab.toUpperCase()}
          </button>
        ))}
      </nav>

      {/* Main */}
      <main className="flex-1 overflow-hidden flex flex-col p-6">
        {activeTab === "ingest" ? (
          <p style={{ color: "#64748b", fontFamily: "JetBrains Mono", fontSize: 12 }}>
            Ingest panel coming soon
          </p>
        ) : (
          <p style={{ color: "#64748b", fontFamily: "JetBrains Mono", fontSize: 12 }}>
            Chat panel coming soon
          </p>
        )}
      </main>

      {/* Footer */}
      <footer
        className="flex items-center gap-3 px-6 py-2 border-t"
        style={{ borderColor: "#1e2430", background: "#0e1014" }}
      >
        <span style={{ fontSize: 10, color: "#64748b", fontFamily: "JetBrains Mono" }}>
          GPT-4o-mini · text-embedding-3-small · ChromaDB · LangChain · FastAPI
        </span>
      </footer>

      <style>{`@keyframes blink { 50% { opacity: 0; } }`}</style>
    </div>
  )
}