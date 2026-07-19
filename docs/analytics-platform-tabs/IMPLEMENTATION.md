# Analytics Platform Tabs Implementation Plan

## Overview

Redesign analytics dashboard with platform-specific tabs showing unique metrics per platform. Each tab has KPIs and charts tailored to that platform's content format.

## Prerequisites

- Backend running with PostgreSQL
- Frontend build working
- Recharts installed (already is)

## Phase Summary

| Phase | Title | Effort |
|-------|-------|--------|
| 1 | Backend: Platform Analytics Endpoint | 1 hour |
| 2 | Frontend: Tab Structure | 30 min |
| 3 | Frontend: Platform KPI Cards | 1 hour |
| 4 | Frontend: Platform Charts | 1.5 hours |
| 5 | Polish & Responsive | 30 min |

---

## Phase 1: Backend Platform Analytics Endpoint

### Objective
Add API endpoint that returns platform-specific metrics.

### Tasks
- [ ] Add `GET /analytics/platform/{platform}` endpoint
- [ ] Query AnalyticsMetric filtered by platform
- [ ] Return platform-specific fields (varies by platform)
- [ ] Add fallback mock data for development

### Success Criteria
- Endpoint returns 200 with platform-specific JSON
- Each platform returns different metric structure

### Files Likely Affected
- `backend/app/api/analytics.py`

---

## Phase 2: Frontend Tab Structure

### Objective
Add tab navigation for platform selection.

### Tasks
- [ ] Add Tabs component to analytics page
- [ ] Create platform list with icons and colors
- [ ] Wire tab state to selected platform
- [ ] Keep "Overview" tab for all-platform view

### Success Criteria
- Tabs render with platform icons
- Clicking tab changes active state
- Layout remains clean

### Files Likely Affected
- `frontend/src/app/dashboard/analytics/page.tsx`

---

## Phase 3: Platform KPI Cards

### Objective
Show platform-specific KPI cards based on selected tab.

### Tasks
- [ ] Define KPI config per platform
- [ ] Create KPI card component
- [ ] Wire KPIs to selected platform
- [ ] Add trend indicators (up/down arrows)

### Success Criteria
- Each platform shows 4 unique KPIs
- KPIs update when switching tabs
- Trend arrows show change vs previous period

### Files Likely Affected
- `frontend/src/app/dashboard/analytics/page.tsx`

---

## Phase 4: Platform Charts

### Objective
Show platform-specific charts based on selected tab.

### Tasks
- [ ] Define chart config per platform
- [ ] Create chart components (line, bar, pie)
- [ ] Wire charts to selected platform
- [ ] Add chart legends and tooltips

### Success Criteria
- Each platform shows 2 relevant charts
- Charts render with correct data
- Tooltips show formatted values

### Files Likely Affected
- `frontend/src/app/dashboard/analytics/page.tsx`

---

## Phase 5: Polish & Responsive

### Objective
Ensure mobile responsiveness and smooth transitions.

### Tasks
- [ ] Test on mobile viewport
- [ ] Add tab scroll on small screens
- [ ] Ensure charts resize properly
- [ ] Add loading states
- [ ] Add empty states for no data

### Success Criteria
- Works on 375px mobile
- Tabs scroll horizontally on mobile
- Charts resize without breaking

### Files Likely Affected
- `frontend/src/app/dashboard/analytics/page.tsx`

---

## Post-Implementation
- [ ] Test with real backend data
- [ ] Add error handling for API failures
- [ ] Consider adding date range picker
- [ ] Consider adding export functionality

## Notes
- Start with mock data, wire to API later
- Keep overview tab for cross-platform comparison
- Use platform colors consistently in charts
