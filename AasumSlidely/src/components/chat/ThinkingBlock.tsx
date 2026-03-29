import { MarkdownRenderer } from "./MarkdownRenderer";

interface ThinkingBlockProps {
  text: string;
}

export function ThinkingBlock({ text }: ThinkingBlockProps) {
  return (
    <div className="msg-appear" style={{ maxWidth: "85%" }}>
      <div style={{ padding: "14px 0", display: "flex", flexDirection: "column", gap: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 14, height: 14, borderRadius: "50%",
            border: "1.5px solid #000", borderTopColor: "transparent",
            animation: "spin 0.8s linear infinite", flexShrink: 0,
          }} />
          <div style={{
            fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
            color: "rgba(0,0,0,0.25)", textTransform: "uppercase",
            letterSpacing: "0.1em",
          }}>
            Thinking
          </div>
        </div>
        {text && (
          <div style={{
            fontSize: 13, fontFamily: "'DM Sans', sans-serif",
            color: "rgba(0,0,0,0.5)", lineHeight: 1.5,
            paddingLeft: 22, maxHeight: 120, overflowY: "auto",
          }}>
            <MarkdownRenderer content={text} dimmed />
          </div>
        )}
      </div>
    </div>
  );
}
