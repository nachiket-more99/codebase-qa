import ReactMarkdown from "react-markdown";
import { useState, useRef, useEffect } from "react";
import { askQuestion } from "@/services/chat";

type Message = {
  role: "user" | "assistant" | "thinking";
  content: string;
  sources?: string[];
};

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const q = text ?? input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setMessages((prev) => [...prev, { role: "thinking", content: "" }]);
    setLoading(true);

    try {
      const data = await askQuestion(q);
      setMessages((prev) => [
        ...prev.filter((m) => m.role !== "thinking"),
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources?.map((s: any) => s.file) ?? [],
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev.filter((m) => m.role !== "thinking"),
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    }

    setLoading(false);
  };

  return (
    <div className="flex h-full gap-4 overflow-hidden">
      {/* Sidebar */}
      <div
        className="flex flex-col gap-4 flex-shrink-0 p-4 rounded"
        style={{
          width: 200,
          background: "#0e1014",
          border: "1px solid #1e2430",
        }}
      >
        <p style={{ fontSize: 10, color: "#475569", fontFamily: "JetBrains Mono", letterSpacing: "0.1em", marginBottom: 8 }}>
  // suggestions
</p>
<div className="flex flex-col gap-1">
  {[
    "What does this codebase do?",
    "How is authentication handled?",
    "Explain the main data models",
    "Where are API endpoints defined?",
    "How does error handling work?",
  ].map((s, i) => (
    <button
      key={i}
      onClick={() => sendMessage(s)}
      disabled={loading}
      className="text-left rounded px-2 py-2 transition-all"
      style={{
        fontFamily: "JetBrains Mono",
        fontSize: 10,
        color: "#64748b",
        border: "1px solid transparent",
        lineHeight: 1.5,
        background: "none",
        cursor: "pointer",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget).style.color = "#00e5a0"
        ;(e.currentTarget).style.borderColor = "#1e2430"
      }}
      onMouseLeave={(e) => {
        (e.currentTarget).style.color = "#64748b"
        ;(e.currentTarget).style.borderColor = "transparent"
      }}
    >
      {s}
    </button>
  ))}
</div>
      </div>

      {/* Main */}
      <div className="flex flex-col flex-1 overflow-hidden gap-3">
        {/* Messages */}
        <div className="flex-1 flex flex-col gap-4 overflow-y-auto pr-1">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-2">
              <p
                style={{
                  fontSize: 13,
                  color: "#475569",
                  fontFamily: "JetBrains Mono",
                }}
              >
                // no messages yet
              </p>
              <p
                style={{
                  fontSize: 11,
                  color: "#475569",
                  fontFamily: "JetBrains Mono",
                }}
              >
                ingest a codebase and start asking questions
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className="flex flex-col gap-1">
              <span
                className="self-start text-xs px-2 py-0.5 rounded"
                style={{
                  fontFamily: "JetBrains Mono",
                  fontSize: 9,
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  background:
                    msg.role === "user"
                      ? "rgba(245,158,11,0.1)"
                      : "rgba(0,229,160,0.1)",
                  color: msg.role === "user" ? "#f59e0b" : "#00e5a0",
                  border: `1px solid ${msg.role === "user" ? "rgba(245,158,11,0.2)" : "rgba(0,229,160,0.2)"}`,
                }}
              >
                {msg.role === "user" ? "YOU" : "GPT-4o-mini"}
              </span>

              <div
                className="rounded-lg px-4 py-3 text-sm"
                style={{
                  fontFamily: "JetBrains Mono",
                  fontSize: 13,
                  lineHeight: 1.7,
                  background: "#0e1014",
                  border: "1px solid #1e2430",
                  borderLeft: `2px solid ${msg.role === "user" ? "#f59e0b" : "#00e5a0"}`,
                  color: "#e2e8f0",
                }}
              >
                {msg.role === "thinking" ? (
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <span
                          key={i}
                          className="inline-block w-1.5 h-1.5 rounded-full"
                          style={{
                            background: "#00e5a0",
                            animation: "pulse 1.2s ease infinite",
                            animationDelay: `${i * 0.2}s`,
                          }}
                        />
                      ))}
                    </div>
                    <span style={{ fontSize: 12, color: "#475569" }}>
                      retrieving context...
                    </span>
                  </div>
                ) : (
                  <div className="prose prose-sm prose-invert max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                )}

                {msg.sources && msg.sources.length > 0 && (
                  <div
                    className="flex flex-wrap gap-2 mt-3 pt-3"
                    style={{ borderTop: "1px solid #1e2430" }}
                  >
                    {[...new Set(msg.sources)].map((source, i) => (
                      <span
                        key={i}
                        style={{
                          fontFamily: "JetBrains Mono",
                          fontSize: 10,
                          padding: "2px 8px",
                          borderRadius: 3,
                          background: "#13161b",
                          border: "1px solid #1e2430",
                          color: "#00a36e",
                        }}
                      >
                        ◆{" "}
                        {(source as string)
                          .replace(/\\/g, "/")
                          .split("/")
                          .slice(-2)
                          .join("/")}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div
          className="flex items-center gap-2 px-4 py-3 rounded"
          style={{ background: "#0e1014", border: "1px solid #1e2430" }}
        >
          <span style={{ color: "#00e5a0", fontSize: 16 }}>$</span>
          <textarea
            className="flex-1 bg-transparent outline-none resize-none text-sm"
            style={{
              fontFamily: "JetBrains Mono",
              color: "#e2e8f0",
              lineHeight: 1.6,
              paddingTop: 0,
              paddingBottom: 0,
              margin: 0,
            }}
            placeholder="ask a question about the codebase..."
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="flex items-center justify-center rounded font-bold transition-all"
            style={{
              width: 36,
              height: 36,
              fontSize: 14,
              background: loading || !input.trim() ? "#0e1014" : "#00e5a0",
              color: loading || !input.trim() ? "#475569" : "#000",
              border: "1px solid #1e2430",
              cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            }}
          >
            →
          </button>
        </div>
        <p
          style={{
            fontSize: 10,
            color: "#475569",
            fontFamily: "JetBrains Mono",
          }}
        >
          Enter to send · Shift+Enter for new line
        </p>
      </div>

      <style>{`@keyframes pulse { 0%, 100% { opacity: 0.2; } 50% { opacity: 1; } }`}</style>
    </div>
  );
}
