import { useState } from "react"

type Mode = "github" | "single" | "multi"

export default function IngestPanel() {
  const [mode, setMode] = useState<Mode>("github")

  return (
    <div className="flex flex-col gap-6 max-w-2xl w-full mx-auto">

      {/* Title */}
      <div>
        <h2 style={{ fontFamily: "Syne", fontWeight: 700, fontSize: 20, color: "#e2e8f0" }}>
          Index Your Codebase
        </h2>
        <p style={{ fontSize: 12, color: "#64748b", marginTop: 4, fontFamily: "JetBrains Mono" }}>
          Point to a GitHub repo or upload source files to begin.
        </p>
      </div>

      {/* Mode switcher */}
      <div
        className="flex gap-1 p-1 rounded"
        style={{ background: "#0e1014", border: "1px solid #1e2430" }}
      >
        {(["github", "single", "multi"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className="flex-1 py-2 rounded text-xs font-semibold tracking-widest transition-all"
            style={{
              fontFamily: "JetBrains Mono",
              background: mode === m ? "#00e5a0" : "transparent",
              color: mode === m ? "#000" : "#64748b",
            }}
          >
            {m === "github" ? "GitHub Repo" : m === "single" ? "Single File" : "Multi File"}
          </button>
        ))}
      </div>

      {/* Placeholder */}
      <p style={{ fontSize: 12, color: "#64748b", fontFamily: "JetBrains Mono" }}>
        Input...
      </p>

    </div>
  )
}