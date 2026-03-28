import type { ThinkingStepData } from "../../types";
import { ThinkingStep } from "./ThinkingStep";

interface ThinkingBlockProps {
  steps: ThinkingStepData[];
  activeStep: number;
  completedSteps: Set<number>;
}

export function ThinkingBlock({ steps, activeStep, completedSteps }: ThinkingBlockProps) {
  return (
    <div className="msg-appear" style={{ maxWidth: "85%" }}>
      <div style={{ padding: "14px 0", display: "flex", flexDirection: "column", gap: 2 }}>
        <div style={{
          fontSize: 10, fontFamily: "'JetBrains Mono', monospace",
          color: "rgba(0,0,0,0.25)", textTransform: "uppercase",
          letterSpacing: "0.1em", marginBottom: 8,
        }}>
          Thinking
        </div>
        {steps.map((step, i) => (
          <ThinkingStep
            key={i}
            step={step}
            isActive={activeStep === i}
            isComplete={completedSteps.has(i)}
          />
        ))}
      </div>
    </div>
  );
}
