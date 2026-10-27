# Redproof site

The static landing page for Redproof. Next.js App Router, TypeScript, Tailwind CSS, `motion`, and `lucide-react`.

## Develop

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Build

```bash
npm run build
```

The static site is written to `site/out`. The build uses `output: "export"`, so the output is plain HTML, CSS, and JavaScript with no server.

## Deploy to Vercel

1. Push this repository to GitHub.
2. In Vercel, choose **Add New → Project** and import the repository.
3. Set **Root Directory** to `site`.
4. Keep the detected framework as Next.js. Build command `npm run build`; output directory `out`.
5. Deploy. No environment variables, backend, or API keys are needed.

The real demo data used by the interactive section lives in `src/data/history.json`, copied from a live Alan run.
