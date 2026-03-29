import { memo, useCallback, useMemo, useRef, useState } from "react";
import { SlidePanelHeader } from "./SlidePanelHeader";

const CANVAS_W = 960;
const CANVAS_H = 540;

interface SlidePanelProps {
  slidesHtml: string | null;
  isGenerating: boolean;
  slideCount: number;
}

function parseSlides(html: string): { styles: string; slides: string[] } {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  const styleTags = doc.querySelectorAll("style");
  const styles = Array.from(styleTags).map((el) => el.innerHTML).join("\n");

  const slideElements = doc.querySelectorAll(".slide");
  const slides = Array.from(slideElements).map((el) => el.outerHTML);

  return { styles, slides };
}

function buildSlideSrcDoc(styles: string, slideHtml: string): string {
  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>${styles}</style></head>
<body style="margin:0;overflow:hidden">${slideHtml}</body>
</html>`;
}

function SlideCard({ srcDoc, index }: { srcDoc: string; index: number }) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  const onWrapperRef = useCallback((node: HTMLDivElement | null) => {
    wrapperRef.current = node;
    if (!node) return;

    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width ?? node.clientWidth;
      setScale(width / CANVAS_W);
    });
    observer.observe(node);
    setScale(node.clientWidth / CANVAS_W);

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={onWrapperRef}
      style={{
        background: "#fff",
        border: "1px solid rgba(0,0,0,0.08)",
        borderRadius: 12,
        marginBottom: 24,
        overflow: "hidden",
        // Height scales proportionally to maintain 16:9
        aspectRatio: "16 / 9",
        position: "relative",
      }}
    >
      <iframe
        srcDoc={srcDoc}
        style={{
          width: CANVAS_W,
          height: CANVAS_H,
          border: "none",
          display: "block",
          transform: `scale(${scale})`,
          transformOrigin: "top left",
        }}
        scrolling="no"
        sandbox="allow-same-origin"
        title={`Slide ${index + 1}`}
      />
    </div>
  );
}

export const SlidePanel = memo(function SlidePanel({ slidesHtml, isGenerating, slideCount }: SlidePanelProps) {
  const { styles, slides } = useMemo(
    () => (slidesHtml ? parseSlides(slidesHtml) : { styles: "", slides: [] }),
    [slidesHtml],
  );

  const slideSrcDocs = useMemo(
    () => slides.map((slideHtml) => buildSlideSrcDoc(styles, slideHtml)),
    [styles, slides],
  );

  return (
    <div className="panel-enter" style={{
      flex: 1, background: "#fff", display: "flex",
      flexDirection: "column", height: "100%",
    }}>
      <SlidePanelHeader isGenerating={isGenerating} slideCount={slideCount} />

      <div className="slide-scroll" style={{
        flex: 1, overflowY: "auto", padding: "20px 24px",
        background: "#fafafa",
      }}>
        {slides.length > 0 ? (
          slides.map((_, index) => (
            <SlideCard key={index} srcDoc={slideSrcDocs[index]} index={index} />
          ))
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
});
