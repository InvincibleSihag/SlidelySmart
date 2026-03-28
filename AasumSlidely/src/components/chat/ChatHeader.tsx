import type { Phase } from "../../types";

interface ChatHeaderProps {
  status: Phase;
  slideCount: number;
}

function getStatusLabel(status: Phase): string {
  switch (status) {
    case "submitting":
    case "queued": return "queued\u2026";
    case "processing": return "generating\u2026";
    case "waiting_for_input": return "waiting for input";
    case "hitl_submitting": return "resuming\u2026";
    case "reconnecting": return "reconnecting\u2026";
    case "failed": return "error";
    case "completed": return "done";
    default: return "ready";
  }
}

export function ChatHeader({ status, slideCount }: ChatHeaderProps) {
  return (
    <div style={{
      padding: "20px 28px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      borderBottom: "1px solid rgba(0,0,0,0.06)", flexShrink: 0,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 10, background: "#000",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="1" y="3" width="14" height="10" rx="1.5" stroke="#fff" strokeWidth="1.2" />
            <line x1="5" y1="7" x2="11" y2="7" stroke="#fff" strokeWidth="1" strokeLinecap="round" />
            <line x1="5" y1="9.5" x2="9" y2="9.5" stroke="#fff" strokeWidth="1" strokeLinecap="round" />
          </svg>
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 600, color: "#000", letterSpacing: "-0.01em" }}>
            Slides Agent
          </div>
          <div style={{
            fontSize: 11, color: "rgba(0,0,0,0.35)",
            fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.02em", marginTop: 1,
          }}>
            {getStatusLabel(status)}
          </div>
        </div>
      </div>
      {slideCount > 0 && (
        <div style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 11, color: "rgba(0,0,0,0.3)", letterSpacing: "0.02em",
        }}>
          {slideCount} slides
        </div>
      )}
    </div>
  );
}
