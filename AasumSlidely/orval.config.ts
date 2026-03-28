import { defineConfig } from "orval";

export default defineConfig({
  slidely: {
    input: {
      target: "http://localhost:9753/openapi.json",
    },
    output: {
      mode: "tags-split",
      target: "src/api/slidely.ts",
      schemas: "src/api/model",
      client: "react-query",
      httpClient: "axios",
      override: {
        mutator: {
          path: "src/lib/axios.ts",
          name: "customInstance",
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
    },
  },
});
