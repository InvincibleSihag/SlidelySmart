import { QueryClientProvider } from "@tanstack/react-query";
import { Routes, Route } from "react-router-dom";
import { queryClient } from "./lib/query-client";
import { SlideAgent } from "./components/SlideAgent";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/" element={<SlideAgent />} />
        <Route path="/:jobId" element={<SlideAgent />} />
      </Routes>
    </QueryClientProvider>
  );
}
