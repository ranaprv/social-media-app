# How to: Use the Analytics Dashboard

Track your social media performance across all connected platforms from one dashboard.

---

## Prerequisites

- At least one social platform connected
- Some published posts (analytics needs data to show)

---

## Dashboard Overview

Navigate to **Analytics** in the sidebar (`/dashboard/analytics`).

The dashboard shows:

### KPI Cards (Top Row)
- **Reach** — Total unique accounts that saw your content
- **Impressions** — Total times your content was displayed
- **Engagement** — Total interactions (likes, comments, shares, clicks)
- **Followers** — Total followers across platforms
- **Engagement Rate** — Engagement / Reach × 100

### Trend Charts
- **Reach over time** — Line chart showing daily/weekly reach
- **Impressions over time** — Line chart showing daily/weekly impressions
- **Engagement over time** — Line chart showing daily/weekly engagement

Toggle between Daily, Weekly, and Monthly views using the time range selector.

### Platform Comparison
Bar chart comparing performance across connected platforms. Quickly see which platform drives the most reach, engagement, or followers.

### Content Distribution
Pie chart showing the breakdown of your content by type (text posts, images, videos, links).

### Best Posting Times
Heatmap showing optimal posting windows — a 7-day × 17-hour grid. Darker cells = higher engagement at that time. Use this to schedule posts when your audience is most active.

### Top Posts
Table listing your best-performing posts with:
- Post title/text
- Platform
- Impressions
- Engagement rate
- Clicks
- Posted date

---

## Filtering

Use the filters at the top of the dashboard to narrow results:
- **Platform**: Show data from specific platforms only
- **Date Range**: Last 7 days, 30 days, 90 days, custom range
- **Content Type**: Posts, Stories, Reels, etc.

---

## Cross-Platform Analytics

The analytics engine aggregates data from all connected platforms into unified metrics. When you connect multiple platforms, the dashboard shows:
- Combined reach across all platforms
- Per-platform breakdowns
- Which platform performs best for each metric

---

## Data Refresh

Analytics data refreshes every 4 hours. If you just published a post, wait a few hours before expecting to see it in analytics.

---

## Exporting Data

1. Click **Export** in the top-right corner of the analytics page
2. Choose format: CSV or PDF
3. The export includes all currently filtered data

---

## Troubleshooting

**No data showing:**
- Ensure at least one platform is connected (see [Connect Social Platforms](connect-social-platforms.md))
- Wait 4+ hours after publishing for analytics data to appear
- Check that your platform connection is still active (tokens may have expired)

**Numbers seem wrong:**
- Platform APIs sometimes lag by 24-48 hours for final metrics
- Instagram insights may not include story views in the standard API
- YouTube analytics update daily, not in real-time

**Missing a platform:**
- Not all platforms provide the same metrics
- YouTube has watch time and subscribers but no "reach" in the same sense as LinkedIn
- The dashboard normalizes metrics where possible
