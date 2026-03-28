import type { HITLSubmitData } from "../../types";

interface HITLSubmittedProps {
  question: string;
  submittedData: HITLSubmitData;
}

export function HITLSubmitted({ question, submittedData }: HITLSubmittedProps) {
  const allChoices = [...(submittedData.selected || [])];
  if (submittedData.custom) allChoices.push(submittedData.custom);

  return (
    <div className="msg-appear" style={{ maxWidth: "88%" }}>
      <div style={{
        padding: "14px 18px", borderRadius: 14,
        background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.05)",
      }}>
        <div style={{
          fontSize: 12, color: "rgba(0,0,0,0.35)", marginBottom: 8,
          fontFamily: "'DM Sans', sans-serif", lineHeight: 1.4,
        }}>
          {question}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
          {allChoices.map((c, i) => (
            <div key={i} style={{
              padding: "5px 13px", borderRadius: 100, background: "#000",
              color: "#fff", fontSize: 12, fontWeight: 500, fontFamily: "'DM Sans', sans-serif",
            }}>
              {c}
            </div>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 8 }}>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <circle cx="6" cy="6" r="5" stroke="rgba(0,0,0,0.15)" strokeWidth="1" />
            <path d="M4 6L5.5 7.5L8 4.5" stroke="rgba(0,0,0,0.3)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span style={{
            fontSize: 10, color: "rgba(0,0,0,0.25)",
            fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.02em",
          }}>
            Submitted
          </span>
        </div>
      </div>
    </div>
  );
}
