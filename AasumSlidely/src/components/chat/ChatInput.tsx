interface ChatInputProps {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  disabled: boolean;
  isWaitingHITL: boolean;
}

export function ChatInput({ input, onInputChange, onSend, onKeyDown, disabled, isWaitingHITL }: ChatInputProps) {
  const canSend = input.trim().length > 0 && !disabled;

  return (
    <div style={{
      padding: "16px 28px 24px",
      borderTop: "1px solid rgba(0,0,0,0.06)", flexShrink: 0,
    }}>
      {isWaitingHITL && (
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          marginBottom: 10, paddingLeft: 2,
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: 3, background: "#000",
            animation: "pulse 1.5s ease-in-out infinite",
          }} />
          <span style={{
            fontSize: 12, color: "rgba(0,0,0,0.35)",
            fontFamily: "'DM Sans', sans-serif",
          }}>
            Answer above to continue
          </span>
        </div>
      )}
      <div style={{
        display: "flex", alignItems: "center", gap: 10,
        background: disabled ? "rgba(0,0,0,0.025)" : "#f5f5f5",
        borderRadius: 14, padding: "4px 4px 4px 18px",
        transition: "background 0.2s ease",
      }}>
        <input
          className="input-field"
          type="text"
          placeholder={disabled ? (isWaitingHITL ? "Complete the form above\u2026" : "Generating\u2026") : "Describe your presentation\u2026"}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={disabled}
          style={{
            flex: 1, border: "none", background: "transparent",
            fontSize: 14, fontFamily: "'DM Sans', sans-serif",
            color: "#000", letterSpacing: "-0.005em",
            opacity: disabled ? 0.4 : 1,
          }}
        />
        <button
          className="send-btn"
          onClick={onSend}
          disabled={!canSend}
          style={{
            width: 36, height: 36, borderRadius: 10, border: "none",
            background: canSend ? "#000" : "rgba(0,0,0,0.08)",
            cursor: canSend ? "pointer" : "default",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0, transition: "all 0.2s ease",
          }}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M3 8H13M13 8L8.5 3.5M13 8L8.5 12.5"
              stroke={canSend ? "#fff" : "rgba(0,0,0,0.2)"}
              strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
