# HMT frontend

React + TypeScript + Vite SPA for the Hyperlocal Misinformation Tracker. Talks to the FastAPI backend in
`../backend/` over REST (see `../ARCHITECTURE.md` for the full system picture).

## Pages

Home · Analyze Claim · Dashboard · Map · Claims (list + search/filter) · Claim Details · Alerts · About

## Develop

```bash
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

Requires the backend running separately (`cd ../backend && uvicorn app.main:app --reload`).

## Other commands

```bash
npm run build   # tsc -b && vite build -> dist/
npm run test    # vitest run
npm run lint    # oxlint
npm run preview # serve the production build locally
```

## Stack notes

- **Charts:** Recharts, styled from the same palette as the rest of the UI (see `src/components/charts/chartTokens.ts`)
- **Map:** Leaflet + OpenStreetMap tiles, no API key. Lazy-loaded (own route chunk) since it's the heaviest dependency.
- **Server state:** TanStack React Query for all API data (caching, loading/error states, refetch); plain `useState` for local UI state (filters, form text). No global client-state store -- this app is almost entirely server-state display.
- **Design tokens:** `src/index.css` defines the light/dark palette as CSS custom properties, following `prefers-color-scheme`.
