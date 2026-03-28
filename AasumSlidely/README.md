# Slidely Frontend

React SPA for the Slidely presentation generator.

## Prerequisites

- Node.js >= 18
- Backend running at http://localhost:9753 (see parent directory)

## Setup

```bash
npm install
cp .env.example .env      # adjust values if needed
npm run api:generate       # generate API client from OpenAPI schema (requires backend running)
npm run dev                # start dev server at http://localhost:3000
```

## Scripts

| Command                | Description                                     |
|------------------------|-------------------------------------------------|
| `npm run dev`          | Start Vite dev server (port 3000)               |
| `npm run build`        | Type-check + production build to `dist/`        |
| `npm run preview`      | Preview production build locally                |
| `npm run lint`         | Run ESLint                                      |
| `npm run api:generate` | Regenerate API client from backend OpenAPI spec |

## API Client Generation

This project uses [orval](https://orval.dev) to auto-generate TypeScript API
client code and TanStack Query hooks from the FastAPI backend's OpenAPI schema.

The generated code lives in `src/api/` and is gitignored. To regenerate:

1. Ensure the backend is running (`uvicorn app.main:app --port 9753`)
2. Run `npm run api:generate`

## Stack

- **React 19** + **TypeScript**
- **Vite 6** (build + dev server)
- **TanStack Query v5** (server state)
- **Zustand v5** (client state)
- **Tailwind CSS v4** (styling)
- **Axios** (HTTP, via orval-generated client)
- **Pusher** (real-time status notifications)
- **orval** (OpenAPI code generation)
