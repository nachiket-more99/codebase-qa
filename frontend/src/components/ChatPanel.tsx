import { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "assistant" | "thinking";
  content: string;
  sources?: string[];
};

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
        <p
          style={{
            fontSize: 10,
            color: "#334155",
            fontFamily: "JetBrains Mono",
            letterSpacing: "0.1em",
          }}
        >
          // suggestions
        </p>
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
                  color: "#334155",
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
          <div ref={bottomRef} />
        </div>

        {/* Input placeholder */}
        <div
          className="flex items-center gap-2 px-4 py-3 rounded"
          style={{ background: "#0e1014", border: "1px solid #1e2430" }}
        >
          <span style={{ color: "#00e5a0", fontSize: 16 }}>$</span>
          <span
            style={{
              fontSize: 12,
              color: "#334155",
              fontFamily: "JetBrains Mono",
            }}
          >
            input coming next...
          </span>
        </div>
      </div>
    </div>
  );
}
