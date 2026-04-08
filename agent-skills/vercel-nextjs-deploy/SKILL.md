---
name: vercel-nextjs-deploy
description: Deploy Next.js applications to Vercel with environment configuration, preview deployments, and production checks. Use when setting up or managing Vercel deployments.
---

# Vercel + Next.js Deployment

## Use When

- Setting up initial Vercel deployment for a Next.js app.
- Configuring environment variables for preview and production.
- Troubleshooting build failures or routing issues.

## Setup Workflow

1. Install Vercel CLI: `npm i -g vercel`.
2. Link project: `vercel link`.
3. Set environment variables: `vercel env add NEXT_PUBLIC_API_URL`.
4. Deploy preview: `vercel` (automatic from branch push).
5. Deploy production: `vercel --prod`.

## Configuration

- `vercel.json` for rewrites, headers, and build settings.
- Environment variables: separate values for preview vs production.
- API routes: `/api/*` handlers deploy as serverless functions.

## Checks Before Deploy

- `npm run build` passes locally.
- No hard-coded localhost URLs in production code.
- Environment variables are set for the target environment.
- Image optimization configured for external domains.

## Monitoring

- Check deployment logs in Vercel dashboard.
- Monitor serverless function cold starts.
- Set up alerts for error rate spikes.
