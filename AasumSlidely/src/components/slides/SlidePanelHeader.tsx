interface SlidePanelHeaderProps {
  isGenerating: boolean;
}

export function SlidePanelHeader({ isGenerating }: SlidePanelHeaderProps) {
  return (
    <div style={{
      height: 64, padding: "0 24px", boxSizing: "border-box" as const,
      display: "flex", alignItems: "center",
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
    </div>
  );
}
