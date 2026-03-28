interface EmptyStateProps {
  onSuggestionClick: (text: string) => void;
}

const SUGGESTIONS = [
  "Pitch deck for a startup",
  "Quarterly review",
  "Design philosophy talk",
];

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", gap: 16,
      animation: "fadeUp 0.6s ease forwards",
    }}>
      <div style={{
        width: 48, height: 48, borderRadius: 14,
        border: "1.5px solid rgba(0,0,0,0.08)",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
          <rect x="2" y="4" width="18" height="14" rx="2" stroke="rgba(0,0,0,0.2)" strokeWidth="1.2" />
          <line x1="7" y1="10" x2="15" y2="10" stroke="rgba(0,0,0,0.15)" strokeWidth="1" strokeLinecap="round" />
          <line x1="7" y1="13" x2="12" y2="13" stroke="rgba(0,0,0,0.15)" strokeWidth="1" strokeLinecap="round" />
        </svg>
      </div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 16, fontWeight: 500, color: "#000", letterSpacing: "-0.01em" }}>
          Create a Presentation
        </div>
        <div style={{ fontSize: 13, color: "rgba(0,0,0,0.35)", marginTop: 6, lineHeight: 1.5 }}>
          Describe what you need and the agent<br />will craft your slides in real time.
        </div>
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap", justifyContent: "center" }}>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestionClick(s)}
            style={{
              padding: "7px 14px", borderRadius: 100,
              border: "1px solid rgba(0,0,0,0.1)", background: "transparent",
              fontSize: 12, color: "rgba(0,0,0,0.5)", cursor: "pointer",
              fontFamily: "'DM Sans', sans-serif", transition: "all 0.2s ease",
            }}
            onMouseOver={(e) => {
              (e.target as HTMLButtonElement).style.borderColor = "rgba(0,0,0,0.3)";
              (e.target as HTMLButtonElement).style.color = "#000";
            }}
            onMouseOut={(e) => {
              (e.target as HTMLButtonElement).style.borderColor = "rgba(0,0,0,0.1)";
              (e.target as HTMLButtonElement).style.color = "rgba(0,0,0,0.5)";
            }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
