import { useState } from "react"
import { API_BASE } from "@/config"

type Mode = "github" | "single" | "multi"

export default function IngestPanel() {
  const [mode, setMode] = useState<Mode>("github")
  const [githubUrl, setGithubUrl] = useState("")
  const [files, setFiles] = useState<File[]>([])

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

      {/* GitHub input */}
      {mode === "github" && (
        <div
          className="flex items-center gap-2 px-4 rounded"
          style={{ background: "#0e1014", border: "1px solid #1e2430" }}
        >
          <span style={{ color: "#00e5a0", fontSize: 14 }}>$</span>
          <input
            className="flex-1 bg-transparent outline-none py-3 text-sm"
            style={{ fontFamily: "JetBrains Mono", color: "#e2e8f0" }}
            placeholder="https://github.com/user/repo"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
          />
        </div>
      )}

      {/* File upload */}
      {(mode === "single" || mode === "multi") && (
        <label
          className="flex flex-col items-center justify-center gap-2 rounded cursor-pointer transition-all"
          style={{ border: "1px dashed #1e2430", padding: "32px 24px", background: "#0e1014" }}
        >
          <span style={{ fontSize: 24, color: "#00e5a0" }}>⬆</span>
          <span style={{ fontSize: 13, color: "#64748b", fontFamily: "JetBrains Mono" }}>
            {files.length > 0
              ? files.map((f) => f.name).join(", ")
              : "Click to browse files"}
          </span>
          <span style={{ fontSize: 10, color: "#334155", fontFamily: "JetBrains Mono" }}>
            .py .ts .js .go .rs .md and more
          </span>
          <input
            type="file"
            multiple={mode === "multi"}
            className="hidden"
            onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
          />
        </label>
      )}

    </div>
  )
}