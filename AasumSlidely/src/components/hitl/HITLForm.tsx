import { useState } from "react";
import type { HITLRequest, HITLSubmitData } from "../../types";
import { HITLSubmitted } from "./HITLSubmitted";

interface HITLFormProps {
  hitl: HITLRequest;
  onSubmit: (data: HITLSubmitData) => void;
  isSubmitted: boolean;
  submittedData: HITLSubmitData | null;
}

export function HITLForm({ hitl, onSubmit, isSubmitted, submittedData }: HITLFormProps) {
  const [selected, setSelected] = useState<string[] | string | null>(
    hitl.form_type === "multi_choice" ? [] : null
  );
  const [customText, setCustomText] = useState("");
  const isSingle = hitl.form_type === "single_choice";

  const toggleOption = (opt: string) => {
    if (isSubmitted) return;
    if (isSingle) {
      setSelected(selected === opt ? null : opt);
    } else {
      setSelected((prev) => {
        const arr = prev as string[];
        return arr.includes(opt) ? arr.filter((o) => o !== opt) : [...arr, opt];
      });
    }
  };

  const hasSelection = isSingle ? selected !== null : (selected as string[]).length > 0;
  const canSubmit = hasSelection || customText.trim().length > 0;

  const handleSubmit = () => {
    if (!canSubmit || isSubmitted) return;
    onSubmit({
      selected: isSingle ? (selected ? [selected as string] : []) : (selected as string[]),
      custom: customText.trim(),
    });
  };

  if (isSubmitted && submittedData) {
    return <HITLSubmitted question={hitl.question} submittedData={submittedData} />;
  }

  const isOptionSelected = (opt: string) =>
    isSingle ? selected === opt : (selected as string[]).includes(opt);

  return (
    <div className="msg-appear" style={{ maxWidth: "88%", width: "100%" }}>
      <div style={{
        border: "1px solid rgba(0,0,0,0.1)", borderRadius: 16,
        overflow: "hidden", background: "#fff",
      }}>
        {/* Header */}
        <div style={{ padding: "18px 20px 14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <div style={{
              width: 20, height: 20, borderRadius: 6, background: "rgba(0,0,0,0.04)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                <circle cx="5.5" cy="5.5" r="4.5" stroke="rgba(0,0,0,0.25)" strokeWidth="1" />
                <path d="M5.5 3.5V5.5H7.5" stroke="rgba(0,0,0,0.25)" strokeWidth="1" strokeLinecap="round" />
              </svg>
            </div>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: 9,
              letterSpacing: "0.12em", textTransform: "uppercase", color: "rgba(0,0,0,0.3)",
            }}>
              {isSingle ? "Select one" : "Select multiple"}
            </div>
          </div>
          <div style={{
            fontSize: 15, fontWeight: 500, color: "#000", lineHeight: 1.4, letterSpacing: "-0.01em",
          }}>
            {hitl.question}
          </div>
        </div>

        {/* Options */}
        {hitl.options && (
          <div style={{ padding: "0 12px 2px", display: "flex", flexDirection: "column", gap: 2 }}>
            {hitl.options.map((opt) => {
              const active = isOptionSelected(opt);
              return (
                <button key={opt} onClick={() => toggleOption(opt)} className="hitl-option-btn"
                  style={{
                    display: "flex", alignItems: "center", gap: 12, padding: "11px 12px",
                    borderRadius: 10, border: "none",
                    background: active ? "rgba(0,0,0,0.04)" : "transparent",
                    cursor: "pointer", width: "100%", textAlign: "left",
                    fontFamily: "'DM Sans', sans-serif", transition: "all 0.15s ease",
                  }}
                >
                  <div style={{
                    width: 18, height: 18, borderRadius: isSingle ? 9 : 5,
                    border: active ? "none" : "1.5px solid rgba(0,0,0,0.15)",
                    background: active ? "#000" : "transparent",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0, transition: "all 0.15s ease",
                  }}>
                    {active && isSingle && (
                      <div style={{ width: 6, height: 6, borderRadius: 3, background: "#fff" }} />
                    )}
                    {active && !isSingle && (
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                        <path d="M2 5L4 7L8 3" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                  <span style={{
                    fontSize: 13.5, color: active ? "#000" : "rgba(0,0,0,0.55)",
                    fontWeight: active ? 500 : 400, transition: "all 0.15s ease",
                  }}>
                    {opt}
                  </span>
                </button>
              );
            })}
          </div>
        )}

        {/* Divider */}
        <div style={{ height: 1, background: "rgba(0,0,0,0.05)", margin: "6px 20px" }} />

        {/* Custom text */}
        <div style={{ padding: "8px 20px 10px" }}>
          <div style={{
            display: "flex", alignItems: "center",
            background: "rgba(0,0,0,0.025)", borderRadius: 8, padding: "0 12px",
          }}>
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style={{ flexShrink: 0 }}>
              <path d="M2 10.5L5 2.5L8 10.5" stroke="rgba(0,0,0,0.18)" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round" />
              <line x1="3" y1="8" x2="7" y2="8" stroke="rgba(0,0,0,0.18)" strokeWidth="1.1" strokeLinecap="round" />
              <line x1="10" y1="5" x2="10" y2="10.5" stroke="rgba(0,0,0,0.18)" strokeWidth="1.1" strokeLinecap="round" />
            </svg>
            <input
              type="text"
              placeholder="Or type something else\u2026"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleSubmit(); }}
              className="input-field"
              style={{
                flex: 1, border: "none", background: "transparent",
                fontSize: 13, fontFamily: "'DM Sans', sans-serif",
                color: "#000", padding: "9px 8px", outline: "none",
              }}
            />
          </div>
        </div>

        {/* Submit */}
        <div style={{ padding: "2px 20px 16px" }}>
          <button onClick={handleSubmit} disabled={!canSubmit} className="hitl-submit"
            style={{
              width: "100%", padding: "10px 16px", borderRadius: 10, border: "none",
              background: canSubmit ? "#000" : "rgba(0,0,0,0.06)",
              color: canSubmit ? "#fff" : "rgba(0,0,0,0.2)",
              fontSize: 13, fontWeight: 500, fontFamily: "'DM Sans', sans-serif",
              cursor: canSubmit ? "pointer" : "default",
              transition: "all 0.2s ease", letterSpacing: "-0.005em",
            }}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
