# ── Dev stage: dependencies only, source mounted via volume ──
FROM node:22-alpine AS dev

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# ── Production build ─────────────────────────────────────────
FROM dev AS build

COPY . .

ARG VITE_API_BASE_URL
ARG VITE_PUSHER_KEY
ARG VITE_PUSHER_CLUSTER

RUN npm run build

# ── Production serve ─────────────────────────────────────────
FROM node:22-alpine

RUN npm install -g serve@14

WORKDIR /app
COPY --from=build /app/dist ./dist

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
