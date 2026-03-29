import { useRef, useEffect, useCallback, useState } from "react";

const MAX_ROWS = 6;
const LINE_HEIGHT = 22;
const VERTICAL_PADDING = 24; // 12px top + 12px bottom

interface ChatInputProps {
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
  disabled: boolean;
  isWaitingHITL: boolean;
}

export function ChatInput({ input, onInputChange, onSend, onKeyDown, disabled, isWaitingHITL }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const canSend = input.trim().length > 0 && !disabled;

  const resize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    const maxHeight = LINE_HEIGHT * MAX_ROWS + VERTICAL_PADDING;
    el.style.height = `${Math.min(el.scrollHeight, maxHeight)}px`;
    el.style.overflowY = el.scrollHeight > maxHeight ? "auto" : "hidden";
  }, []);

  useEffect(resize, [input, resize]);

  // Auto-focus when not disabled
  useEffect(() => {
    if (!disabled) textareaRef.current?.focus();
  }, [disabled]);

  const placeholder = disabled
    ? (isWaitingHITL ? "Complete the form above\u2026" : "Generating\u2026")
    : "Describe your presentation\u2026";

  return (
    <div style={{
      padding: "12px 24px 20px",
      flexShrink: 0,
    }}>
      {isWaitingHITL && (
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          marginBottom: 10, paddingLeft: 4,
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

      <div
        className="chat-input-container"
        style={{
          position: "relative",
          display: "flex",
          alignItems: "flex-end",
          gap: 8,
          background: disabled ? "rgba(0,0,0,0.02)" : (isFocused ? "#fff" : "#f8f8f8"),
          borderRadius: 20,
          padding: "6px 6px 6px 20px",
          border: `1px solid ${isFocused && !disabled ? "rgba(0,0,0,0.12)" : "rgba(0,0,0,0.06)"}`,
          boxShadow: isFocused && !disabled
            ? "0 0 0 3px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.04)"
            : "0 1px 3px rgba(0,0,0,0.02)",
          transition: "all 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        <textarea
          ref={textareaRef}
          className="input-field"
          rows={1}
          placeholder={placeholder}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={onKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          style={{
            flex: 1,
            border: "none",
            background: "transparent",
            fontSize: 14,
            fontFamily: "'DM Sans', sans-serif",
            color: "#000",
            letterSpacing: "-0.005em",
            lineHeight: `${LINE_HEIGHT}px`,
            padding: "12px 0",
            resize: "none",
            overflowY: "hidden",
            opacity: disabled ? 0.4 : 1,
            transition: "opacity 0.2s ease",
          }}
        />

        <button
          className="send-btn"
          onClick={onSend}
          disabled={!canSend}
          aria-label="Send message"
          style={{
            width: 36,
            height: 36,
            borderRadius: 12,
            border: "none",
            background: canSend ? "#000" : "rgba(0,0,0,0.06)",
            cursor: canSend ? "pointer" : "default",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            transition: "all 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
            transform: canSend ? "scale(1)" : "scale(0.92)",
            marginBottom: 2,
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            style={{ 
              transition: "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
              transform: canSend ? "translateY(-0.5px)" : "none",
            }}
          >
            <path
              d="M8 13V3M8 3L3.5 7.5M8 3L12.5 7.5"
              stroke={canSend ? "#fff" : "rgba(0,0,0,0.15)"}
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <div style={{
        display: "flex",
        justifyContent: "flex-end",
        padding: "6px 4px 0",
      }}>
        <span style={{
          fontSize: 11,
          color: "rgba(0,0,0,0.2)",
          fontFamily: "'JetBrains Mono', monospace",
          letterSpacing: "0.01em",
          userSelect: "none",
          transition: "opacity 0.2s ease",
          opacity: isFocused && !disabled ? 1 : 0,
        }}>
          shift + enter for new line
        </span>
      </div>
    </div>
  );
}
