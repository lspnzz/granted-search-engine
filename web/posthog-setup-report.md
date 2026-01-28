# PostHog post-wizard report

The wizard has completed a deep integration of PostHog analytics into your Granted EU grants search engine project. The integration includes:

- **Client-side tracking** via `instrumentation-client.ts` using the modern Next.js 15.3+ approach
- **Server-side tracking** via `posthog-node` for API route analytics
- **Reverse proxy configuration** in `next.config.ts` to improve tracking reliability and avoid ad blockers
- **Exception capture** for automatic error tracking
- **Custom events** tracking key user interactions throughout the search flow

## Events Implemented

| Event Name | Description | File |
|------------|-------------|------|
| `grant_searched` | User performed a grant search with their project pitch | `app/page.tsx` |
| `grant_card_expanded` | User expanded a grant card to view more details | `app/page.tsx` |
| `grant_source_clicked` | User clicked through to the EU Funding & Tenders Portal | `components/GrantCard.tsx` |
| `search_error` | Client-side search request failed | `app/page.tsx` |
| `menu_toggled` | User toggled the navigation menu | `components/Navbar.tsx` |
| `server_search_completed` | Server-side: Grant search API completed successfully | `app/api/search/route.ts` |
| `server_search_error` | Server-side: Grant search API failed with an error | `app/api/search/route.ts` |

## Files Created/Modified

| File | Change |
|------|--------|
| `instrumentation-client.ts` | Created - PostHog client-side initialization |
| `lib/posthog-server.ts` | Created - Server-side PostHog client |
| `next.config.ts` | Modified - Added reverse proxy rewrites for PostHog EU |
| `.env.local` | Modified - Added PostHog environment variables |
| `app/page.tsx` | Modified - Added search and card expansion tracking |
| `components/GrantCard.tsx` | Modified - Added source link click tracking |
| `components/Navbar.tsx` | Modified - Added menu toggle tracking |
| `app/api/search/route.ts` | Modified - Added server-side search tracking |

## Next steps

We've built some insights and a dashboard for you to keep an eye on user behavior, based on the events we just instrumented:

### Dashboard
- [Analytics basics](https://eu.posthog.com/project/120576/dashboard/504142) - Main analytics dashboard

### Insights
- [Grant Searches Over Time](https://eu.posthog.com/project/120576/insights/HN0sj4Rq) - Track search volume trends
- [Search to Grant Click Funnel](https://eu.posthog.com/project/120576/insights/irD8W40V) - Conversion funnel from search to grant source click
- [Search Error Rate](https://eu.posthog.com/project/120576/insights/BQ4EZEDe) - Monitor client and server-side errors
- [Average Results per Search](https://eu.posthog.com/project/120576/insights/pa7apJqV) - Track search quality
- [User Engagement Overview](https://eu.posthog.com/project/120576/insights/YKr2grkA) - Overall engagement metrics

### Agent skill

We've left an agent skill folder in your project at `.claude/skills/nextjs-app-router/`. You can use this context for further agent development when using Claude Code. This will help ensure the model provides the most up-to-date approaches for integrating PostHog.
