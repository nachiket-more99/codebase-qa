import { useState } from "react";
import {
  ingestRepo,
  ingestSingleFile,
  ingestMultipleFiles,
  clearIndex,
} from "@/services/ingest";

type Mode = "github" | "single" | "multi";

type LogEntry = {
  id: number;
  msg: string;
  type: "info" | "success" | "error" | "detail";
};

const logColor = {
  info: "#64748b",
  success: "#00e5a0",
  error: "#ef4444",
  detail: "#334155",
};

export default function IngestPanel({ onComplete }: { onComplete: () => void }) {
  const [mode, setMode] = useState<Mode>("github");
  const [githubUrl, setGithubUrl] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [log, setLog] = useState<LogEntry[]>([]);

  const push = (msg: string, type: LogEntry["type"] = "info") =>
    setLog((prev) => [...prev, { id: Date.now() + Math.random(), msg, type }]);

  const handleIngest = async () => {
    if (loading) return;
    setLoading(true);
    setLog([]);

    try {
      if (mode === "github") {
        if (!githubUrl.trim()) {
          push("Enter a GitHub URL.", "error");
          setLoading(false);
          return;
        }
        push(`Cloning → ${githubUrl}`);
        const data = await ingestRepo(githubUrl);
        push(
          `${data.total_files_ingested} file(s) indexed successfully`,
          "success",
        );

        push(
          `files: ${data.total_files_ingested ?? "?"}  chunks: ${data.total_chunks_created ?? "?"}`,
          "detail",
        );
        push(`✓ ready — switching to chat...`, "success")
setTimeout(() => onComplete(), 1500)
      } else if (mode === "single") {
        if (!files[0]) {
          push("Select a file first.", "error");
          setLoading(false);
          return;
        }
        push(`Uploading → ${files[0].name}`);
        const data = await ingestSingleFile(files[0]);
        push(`${data.file} indexed successfully`, "success");
        push(`chunks: ${data.chunks_created ?? "?"}`, "detail");
        push(`✓ ready — switching to chat...`, "success")
setTimeout(() => onComplete(), 1500)
      } else {
        if (!files.length) {
          push("Select files first.", "error");
          setLoading(false);
          return;
        }
        push(`Uploading ${files.length} files...`);
        const data = await ingestMultipleFiles(files);
        push(
          `${data.total_files_ingested} file(s) indexed successfully`,
          "success",
        );
        push(`✓ ready — switching to chat...`, "success")
setTimeout(() => onComplete(), 1500)
        data.ingested_files?.forEach((f: any) =>
          push(`  ${f.file}: ${f.chunks ?? "?"} chunks`, "detail"),
        );
      }
    } catch (err: any) {
      push(`Error: ${err.message}`, "error");
    }

    setLoading(false);
  };

  const handleClear = async () => {
    if (!confirm("Clear all indexed data?")) return;
    try {
      const data = await clearIndex();
      push(data.message ?? "Index cleared.", "success");
    } catch (err: any) {
      push(`Error: ${err.message}`, "error");
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-2xl w-full mx-auto">
      {/* Title */}
      <div>
        <h2
          style={{
            fontFamily: "Syne",
            fontWeight: 700,
            fontSize: 20,
            color: "#e2e8f0",
          }}
        >
          Index Your Codebase
        </h2>
        <p
          style={{
            fontSize: 12,
            color: "#64748b",
            marginTop: 4,
            fontFamily: "JetBrains Mono",
          }}
        >
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
            {m === "github"
              ? "GitHub Repo"
              : m === "single"
                ? "Single File"
                : "Multi File"}
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
            onKeyDown={(e) => e.key === "Enter" && handleIngest()}
          />
        </div>
      )}

      {/* File upload */}
      {(mode === "single" || mode === "multi") && (
        <label
          className="flex flex-col items-center justify-center gap-2 rounded cursor-pointer transition-all"
          style={{
            border: "1px dashed #1e2430",
            padding: "32px 24px",
            background: "#0e1014",
          }}
        >
          <span style={{ fontSize: 24, color: "#00e5a0" }}>⬆</span>
          <span
            style={{
              fontSize: 13,
              color: "#64748b",
              fontFamily: "JetBrains Mono",
            }}
          >
            {files.length > 0
              ? files.map((f) => f.name).join(", ")
              : "Click to browse files"}
          </span>
          <span
            style={{
              fontSize: 10,
              color: "#334155",
              fontFamily: "JetBrains Mono",
            }}
          >
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

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleIngest}
          disabled={loading}
          className="px-6 py-2 rounded text-xs font-bold tracking-widest transition-all"
          style={{
            fontFamily: "JetBrains Mono",
            background: loading ? "#00a36e" : "#00e5a0",
            color: "#000",
            opacity: loading ? 0.7 : 1,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "INDEXING..." : "RUN INGEST →"}
        </button>
        <button
          onClick={handleClear}
          className="px-6 py-2 rounded text-xs tracking-widest transition-all"
          style={{
            fontFamily: "JetBrains Mono",
            border: "1px solid #1e2430",
            color: "#64748b",
            cursor: "pointer",
          }}
        >
          CLEAR INDEX
        </button>
      </div>

      {/* Terminal log */}
      {log.length > 0 && (
        <div
          className="rounded overflow-hidden"
          style={{ background: "#060709", border: "1px solid #1e2430" }}
        >
          <div
            className="px-4 py-2 border-b"
            style={{ borderColor: "#1e2430", background: "#0e1014" }}
          >
            <span
              style={{
                fontSize: 10,
                color: "#334155",
                letterSpacing: "0.1em",
                fontFamily: "JetBrains Mono",
              }}
            >
              // output
            </span>
          </div>
          {log.map((entry) => (
            <div
              key={entry.id}
              className="flex gap-2 px-4 py-1"
              style={{ fontSize: 12, fontFamily: "JetBrains Mono" }}
            >
              <span style={{ color: "#334155" }}>&gt;</span>
              <span style={{ color: logColor[entry.type] }}>{entry.msg}</span>
            </div>
          ))}
          {loading && (
            <div
              className="px-4 py-1"
              style={{
                fontSize: 12,
                fontFamily: "JetBrains Mono",
                color: "#00e5a0",
              }}
            >
              <span style={{ animation: "blink 0.8s steps(1) infinite" }}>
                █
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
