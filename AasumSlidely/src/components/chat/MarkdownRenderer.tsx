import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

interface MarkdownRendererProps {
  content: string;
  dimmed?: boolean;
}

const components: Components = {
  h1: ({ children }) => (
    <h1 style={{ fontSize: 20, fontWeight: 600, margin: "16px 0 8px", lineHeight: 1.3 }}>
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 style={{ fontSize: 17, fontWeight: 600, margin: "14px 0 6px", lineHeight: 1.3 }}>
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 style={{ fontSize: 15, fontWeight: 600, margin: "12px 0 4px", lineHeight: 1.4 }}>
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p style={{ margin: "6px 0", lineHeight: 1.55 }}>{children}</p>
  ),
  ul: ({ children }) => (
    <ul style={{ margin: "6px 0", paddingLeft: 20, listStyleType: "disc" }}>{children}</ul>
  ),
  ol: ({ children }) => (
    <ol style={{ margin: "6px 0", paddingLeft: 20, listStyleType: "decimal" }}>{children}</ol>
  ),
  li: ({ children }) => (
    <li style={{ margin: "2px 0", lineHeight: 1.55 }}>{children}</li>
  ),
  strong: ({ children }) => (
    <strong style={{ fontWeight: 600 }}>{children}</strong>
  ),
  em: ({ children }) => <em>{children}</em>,
  code: ({ children, className }) => {
    const isBlock = className?.startsWith("language-");
    if (isBlock) {
      return (
        <code
          style={{
            display: "block",
            background: "rgba(0,0,0,0.04)",
            borderRadius: 8,
            padding: "12px 14px",
            fontSize: 13,
            fontFamily: "'JetBrains Mono', monospace",
            overflowX: "auto",
            lineHeight: 1.5,
          }}
        >
          {children}
        </code>
      );
    }
    return (
      <code
        style={{
          background: "rgba(0,0,0,0.06)",
          borderRadius: 4,
          padding: "1px 5px",
          fontSize: 13,
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre style={{ margin: "8px 0", overflow: "auto" }}>{children}</pre>
  ),
  blockquote: ({ children }) => (
    <blockquote
      style={{
        borderLeft: "3px solid rgba(0,0,0,0.15)",
        paddingLeft: 14,
        margin: "8px 0",
        color: "rgba(0,0,0,0.6)",
      }}
    >
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: "#000", textDecoration: "underline", textUnderlineOffset: 2 }}
    >
      {children}
    </a>
  ),
  hr: () => (
    <hr style={{ border: "none", borderTop: "1px solid rgba(0,0,0,0.1)", margin: "12px 0" }} />
  ),
  table: ({ children }) => (
    <div style={{ overflowX: "auto", margin: "8px 0" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 13 }}>
        {children}
      </table>
    </div>
  ),
  th: ({ children }) => (
    <th style={{ borderBottom: "2px solid rgba(0,0,0,0.1)", padding: "6px 10px", textAlign: "left", fontWeight: 600 }}>
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td style={{ borderBottom: "1px solid rgba(0,0,0,0.06)", padding: "6px 10px" }}>
      {children}
    </td>
  ),
};

export function MarkdownRenderer({ content, dimmed }: MarkdownRendererProps) {
  return (
    <div style={dimmed ? { opacity: 0.6 } : undefined}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
