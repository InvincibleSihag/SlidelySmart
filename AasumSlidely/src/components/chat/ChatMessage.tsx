import { MarkdownRenderer } from "./MarkdownRenderer";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  return (
    <div className="msg-appear" style={{
      display: "flex", flexDirection: "column",
      alignItems: role === "user" ? "flex-end" : "flex-start", gap: 4,
    }}>
      <div style={{
        maxWidth: "85%",
        padding: role === "user" ? "10px 16px" : "0",
        borderRadius: role === "user" ? 18 : 0,
        background: role === "user" ? "#000" : "transparent",
        color: role === "user" ? "#fff" : "#000",
        fontSize: 14, lineHeight: 1.55, letterSpacing: "-0.005em",
      }}>
        {role === "assistant" ? <MarkdownRenderer content={content} /> : content}
      </div>
      <div style={{
        fontSize: 10, color: "rgba(0,0,0,0.2)",
        fontFamily: "'JetBrains Mono', monospace",
      }}>
        {formatTime(timestamp)}
      </div>
    </div>
  );
}
