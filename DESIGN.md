# Design System — Social Media Manager

## Brand Identity

**Product:** AI-Powered Social Media Content Management Platform  
**Tagline:** "Content at the speed of thought"  
**Personality:** Professional but approachable. Technical capability with human warmth. For creators who take their work seriously but don't take themselves too seriously.

### Memorable Thing
Every interaction should feel like having a sharp, reliable creative partner — not a tool. The AI suggests, the human decides. Speed without sacrificing quality.

---

## Color System

### Primary Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--primary` | `#3b82f6` | `#3b82f6` | CTAs, links, active states |
| `--secondary` | `#8b5cf6` | `#8b5cf6` | AI features, badges, highlights |
| `--accent` | `#06b6d4` | `#06b6d4` | Data visualization, accents |

### Neutral Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--background` | `#ffffff` | `#0f172a` | Page background |
| `--foreground` | `#0f172a` | `#f8fafc` | Primary text |
| `--muted` | `#f1f5f9` | `#1e293b` | Subtle backgrounds |
| `--muted-foreground` | `#64748b` | `#94a3b8` | Secondary text |
| `--card` | `#ffffff` | `#1e293b` | Card backgrounds |
| `--border` | `#e2e8f0` | `#334155` | Borders, dividers |

### Semantic Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--destructive` | `#ef4444` | `#ef4444` | Errors, delete actions |
| `--success` | `#22c55e` | `#22c55e` | Success states, positive metrics |
| `--warning` | `#f59e0b` | `#f59e0b` | Warnings, pending states |

### Platform Colors (for data viz)

| Platform | Color | Hex |
|----------|-------|-----|
| LinkedIn | Blue | `#0A66C2` |
| X (Twitter) | Black | `#000000` |
| Instagram | Gradient | `#E4405F` |
| Facebook | Blue | `#1877F2` |
| YouTube | Red | `#FF0000` |

### Color Rules
- Never use more than 3 accent colors per screen
- Status colors = severity, not decoration
- Neutral states use grey, not colored
- All colors pass WCAG AA contrast (4.5:1 for text)

---

## Typography

### Font Stack

```css
--font-sans: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Geist Mono', 'SF Mono', 'Fira Code', monospace;
```

### Type Scale

| Name | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| `display` | 48px | 700 | 1.1 | Hero headlines |
| `h1` | 36px | 700 | 1.2 | Page titles |
| `h2` | 24px | 600 | 1.3 | Section headers |
| `h3` | 20px | 600 | 1.4 | Card titles |
| `body` | 16px | 400 | 1.5 | Default text |
| `body-sm` | 14px | 400 | 1.5 | Secondary text |
| `caption` | 12px | 500 | 1.4 | Labels, metadata |
| `overline` | 11px | 600 | 1.5 | Category labels, uppercase |

### Typography Rules
- Display/headings: `tracking-tight` (-0.02em)
- Body text: no custom tracking
- Captions: `uppercase tracking-wider` (0.05em)
- Never use `line-height: 1.5` on display text (too loose)
- Min text size: 12px on mobile

---

## Spacing

### Scale (4px base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps (icon + text) |
| `space-2` | 8px | Form field gaps |
| `space-3` | 12px | Card padding (compact) |
| `space-4` | 16px | Standard padding |
| `space-5` | 20px | Section gaps |
| `space-6` | 24px | Card padding (default) |
| `space-8` | 32px | Section spacing |
| `space-10` | 40px | Page margins |
| `space-12` | 48px | Major section breaks |

### Spacing Rules
- All spacing must be multiples of 4px
- No arbitrary values (no `p-[13px]`)
- Use logical properties (`ms-*`/`me-*` not `ml-*`/`mr-*`)
- Consistent within components (all cards same padding)

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-sm` | 4px | Small elements (badges, tags) |
| `rounded` | 6px | Inputs, buttons |
| `rounded-lg` | 8px | Cards, modals |
| `rounded-xl` | 12px | Feature cards, containers |
| `rounded-2xl` | 16px | Hero sections, major containers |
| `rounded-full` | 9999px | Avatars, pills, circular buttons |

### Radius Rules
- One radius personality per page (don't mix sharp + soft)
- Nested elements: inner radius = outer radius - padding
- Buttons and inputs share the same radius

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |
| `shadow` | `0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)` | Cards, dropdowns |
| `shadow-md` | `0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)` | Modals, popovers |
| `shadow-lg` | `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` | Floating elements |

### Shadow Rules
- Same light direction everywhere (top-down)
- Never mix black shadows with tinted shadows
- Use `shadow-sm` as default, escalate for importance

---

## Components

### Button

| Variant | Background | Text | Border | Usage |
|---------|------------|------|--------|-------|
| `default` | Primary | White | None | Primary actions |
| `destructive` | Red | White | None | Delete, danger |
| `outline` | Transparent | Foreground | Border | Secondary actions |
| `secondary` | Purple | White | None | AI features |
| `ghost` | Transparent | Foreground | None | Navigation, minimal |
| `link` | Transparent | Primary | None | Inline actions |

| Size | Height | Padding | Usage |
|------|--------|---------|-------|
| `sm` | 36px | 12px | Compact UI |
| `default` | 40px | 16px | Standard |
| `lg` | 44px | 32px | Hero CTAs |
| `icon` | 40px | - | Icon-only |

### Input

- Height: 40px
- Border: 1px solid `--border`
- Focus ring: 2px solid `--ring` with offset
- Placeholder: `--muted-foreground`
- Error state: `--destructive` border

### Card

- Background: `--card`
- Border: 1px solid `--border`
- Radius: `rounded-xl` (12px)
- Padding: 24px (default), 16px (compact)
- Hover: `shadow-md` transition

### Modal/Dialog

- Backdrop: `black/50` with blur
- Card: `--card` background, `rounded-2xl`
- Max width: 480px (sm), 640px (md), 800px (lg)
- Close button: top-right, ghost variant

### Badge/Tag

- Height: 24px
- Padding: 0 10px
- Radius: `rounded-full`
- Font: 12px, weight 500
- Colors: Platform-specific or semantic

---

## Icons

**Library:** Lucide React  
**Style:** Outlined, stroke-width 2  
**Size:** 16px (inline), 20px (buttons), 24px (navigation)

### Icon Rules
- One icon family across the app
- No emoji as UI icons
- Consistent stroke weight (2px)
- Use `currentColor` for automatic theming

---

## Layout

### Grid System

- Max width: 1280px (container)
- Columns: 12 (desktop), 8 (tablet), 4 (mobile)
- Gutter: 24px
- Margin: auto on container

### Sidebar Navigation

- Width: 256px (expanded), 64px (collapsed)
- Background: `--card`
- Border-right: 1px solid `--border`
- Item height: 40px
- Active state: `--primary` background

### Dashboard Layout

```
┌─────────────────────────────────────┐
│ Header (64px)                       │
├──────────┬──────────────────────────┤
│ Sidebar  │ Main Content            │
│ (256px)  │ (flex-1, padding: 24px) │
│          │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

---

## Motion

### Transitions

| Property | Duration | Easing | Usage |
|----------|----------|--------|-------|
| Colors | 150ms | ease | Theme changes |
| Transform | 200ms | ease-out | Hover effects |
| Opacity | 200ms | ease | Fade in/out |
| Slide | 300ms | ease-in-out | Panel open/close |

### Animation Rules
- Respect `prefers-reduced-motion`
- No animation on page load (distracting)
- Subtle hover effects (scale 1.02, shadow lift)
- Loading states: skeleton screens, not spinners (when possible)

---

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, stacked |
| Tablet | 640-1024px | 2-column grid |
| Desktop | > 1024px | Full sidebar + content |
| Wide | > 1280px | Max container width |

### Mobile Rules
- No horizontal overflow
- Touch targets ≥ 44px
- Text ≥ 12px
- Safe area insets for notched devices
- Simplified navigation (bottom bar or hamburger)

---

## Accessibility

### Requirements
- All interactive elements keyboard-focusable
- Focus visible: 2px ring with offset
- Color contrast: 4.5:1 (text), 3:1 (large text)
- ARIA labels on icon-only buttons
- Form inputs associated with labels
- Error messages linked to inputs
- Skip navigation link
- Reduced motion support

---

## Dark Mode

### Implementation
- Toggle via `ThemeProvider`
- CSS variables swap in `.dark` class
- No flash on load (SSR-compatible)
- System preference detection

### Dark Mode Adjustments
- Background: `#0f172a` (slate-900)
- Cards: `#1e293b` (slate-800)
- Borders: `#334155` (slate-700)
- Text: `#f8fafc` (slate-50)
- Muted text: `#94a3b8` (slate-400)

---

## File Structure

```
src/
├── app/
│   ├── globals.css          # Design tokens
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── components/
│   ├── ui/                  # Primitives (Button, Input, Card)
│   ├── layout/              # Sidebar, Header, DashboardLayout
│   ├── content-studio/      # AI content features
│   ├── calendar/            # Scheduling UI
│   ├── analytics/           # Charts, metrics
│   └── providers/           # Theme, Auth
└── lib/
    └── utils.ts             # cn() helper
```

---

## Design Principles

1. **Clarity over cleverness** — Users should understand the UI instantly
2. **Consistency builds trust** — Same patterns everywhere
3. **Content is king** — UI recedes, content advances
4. **Speed matters** — Fast interactions, fast loading, fast learning
5. **Accessible by default** — Not an afterthought

---

## Future Considerations

### Animation Library
- Add Framer Motion for page transitions
- Implement skeleton loading states
- Add micro-interactions (button press, card flip)

### Illustration Style
- Line art, 2px stroke
- Monochrome with primary accent
- Friendly but professional

### Data Visualization
- Chart.js or Recharts (already installed)
- Consistent color coding by platform
- Responsive chart containers

---

*Last updated: July 2026*  
*Version: 1.0*
