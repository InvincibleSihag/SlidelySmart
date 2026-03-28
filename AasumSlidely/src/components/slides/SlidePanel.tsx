import { SlidePanelHeader } from "./SlidePanelHeader";

interface SlidePanelProps {
  slidesHtml: string | null;
  isGenerating: boolean;
  slideCount: number;
}

export function SlidePanel({ slidesHtml, isGenerating, slideCount }: SlidePanelProps) {
  return (
    <div className="panel-enter" style={{
      flex: 1, background: "#fff", display: "flex",
      flexDirection: "column", height: "100%",
    }}>
      <SlidePanelHeader isGenerating={isGenerating} slideCount={slideCount} />

      <div className="slide-scroll" style={{
        flex: 1, overflowY: "auto", padding: "20px 24px",
      }}>
        {slidesHtml ? (
          <div dangerouslySetInnerHTML={{ __html: slidesHtml }} />
        ) : isGenerating ? (
          <div style={{ textAlign: "center", padding: "20px 0", animation: "fadeUp 0.4s ease forwards" }}>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 10, color: "rgba(0,0,0,0.2)",
              letterSpacing: "0.08em", textTransform: "uppercase",
            }}>
              Generating slides
            </div>
            <div style={{
              width: 120, height: 2, background: "rgba(0,0,0,0.06)",
              borderRadius: 1, margin: "10px auto 0", overflow: "hidden",
            }}>
              <div style={{
                width: "30%",
                height: "100%", background: "#000", borderRadius: 1,
                animation: "pulse 1.5s ease-in-out infinite",
              }} />
            </div>
          </div>
        ) : (
          <div style={{
            flex: 1, display: "flex", alignItems: "center", justifyContent: "center",
            color: "rgba(0,0,0,0.2)", fontSize: 13,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Slides will appear here
          </div>
        )}
      </div>
    </div>
  );
}
