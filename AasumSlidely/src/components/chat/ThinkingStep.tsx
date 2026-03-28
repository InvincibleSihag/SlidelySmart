import type { ThinkingStepData } from "../../types";

interface ThinkingStepProps {
  step: ThinkingStepData;
  isActive: boolean;
  isComplete: boolean;
}

export function ThinkingStep({ step, isActive, isComplete }: ThinkingStepProps) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 0" }}>
      <div style={{
        width: 16, height: 16, borderRadius: "50%",
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
      }}>
        {isComplete ? (
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="7" r="7" fill="#000" />
            <path d="M4 7L6 9L10 5" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : isActive ? (
          <div style={{
            width: 14, height: 14, borderRadius: "50%",
            border: "1.5px solid #000", borderTopColor: "transparent",
            animation: "spin 0.8s linear infinite",
          }} />
        ) : (
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: "rgba(0,0,0,0.1)" }} />
        )}
      </div>
      <span style={{
        fontFamily: "'DM Sans', sans-serif", fontSize: 13,
        color: isComplete ? "#000" : isActive ? "#000" : "rgba(0,0,0,0.25)",
        fontWeight: isActive ? 500 : 400, transition: "color 0.3s ease",
      }}>
        {step.label}
      </span>
    </div>
  );
}
