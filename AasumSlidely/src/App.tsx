import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/query-client";
import { SlideAgent } from "./components/SlideAgent";

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SlideAgent />
    </QueryClientProvider>
  );
}
