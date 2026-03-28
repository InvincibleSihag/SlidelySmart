interface SlidePanelHeaderProps {
  isGenerating: boolean;
  slideCount: number;
}

export function SlidePanelHeader({ isGenerating, slideCount }: SlidePanelHeaderProps) {
  return (
    <div style={{
      padding: "20px 24px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      borderBottom: "1px solid rgba(0,0,0,0.06)", flexShrink: 0,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ fontSize: 14, fontWeight: 500, color: "#000", letterSpacing: "-0.01em" }}>
          Preview
        </div>
        {isGenerating && (
          <div style={{ display: "flex", gap: 3, alignItems: "center" }}>
            {[0, 1, 2].map(i => (
              <div key={i} style={{
                width: 3, height: 3, borderRadius: "50%", background: "#000",
                animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
              }} />
            ))}
          </div>
        )}
      </div>
      {!isGenerating && slideCount > 0 && (
        <button
          style={{
            padding: "6px 14px", borderRadius: 100,
            border: "1px solid rgba(0,0,0,0.12)", background: "transparent",
            fontSize: 12, fontWeight: 500, color: "#000", cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif",
            display: "flex", alignItems: "center", gap: 6, transition: "all 0.2s ease",
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.background = "#000";
            e.currentTarget.style.color = "#fff";
            e.currentTarget.style.borderColor = "#000";
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.color = "#000";
            e.currentTarget.style.borderColor = "rgba(0,0,0,0.12)";
          }}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 2V10M6 10L9 7M6 10L3 7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Export
        </button>
      )}
    </div>
  );
}
