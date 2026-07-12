# Jyothishyam — Frontend Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Framework:** Next.js 14+ (App Router), TypeScript, TailwindCSS

---

## 1. Overview

The frontend is a Next.js application using the **App Router** (not Pages Router). It communicates with the FastAPI backend via REST. Global state is managed by Zustand; server/API data is managed by React Query (TanStack Query v5).

---

## 2. Project Structure

```
frontend/
├── app/
│   ├── layout.tsx                  ← Root layout (fonts, providers, global nav)
│   ├── page.tsx                    ← Home / landing page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── layout.tsx              ← Auth-specific layout (no sidebar)
│   ├── (dashboard)/
│   │   ├── layout.tsx              ← Dashboard layout (sidebar + nav)
│   │   ├── dashboard/page.tsx      ← User dashboard home
│   │   ├── charts/
│   │   │   ├── page.tsx            ← List all charts
│   │   │   ├── new/page.tsx        ← Create new chart form
│   │   │   └── [chartId]/page.tsx  ← View a specific chart
│   │   ├── ai/
│   │   │   ├── page.tsx            ← AI question console
│   │   │   └── history/page.tsx    ← Saved AI readings
│   │   ├── compatibility/
│   │   │   ├── page.tsx            ← Compatibility checker
│   │   │   └── profiles/page.tsx   ← Manage compatibility profiles
│   │   ├── predictions/
│   │   │   └── page.tsx            ← Daily/weekly/monthly predictions
│   │   ├── credits/page.tsx        ← Credit balance + ledger history
│   │   └── profile/page.tsx        ← User profile settings
│   ├── payments/
│   │   ├── page.tsx                ← Pricing / credit packs
│   │   ├── success/page.tsx        ← Post-payment success
│   │   └── cancel/page.tsx         ← Payment cancelled
│   └── globals.css
├── components/
│   ├── charts/
│   │   ├── ChartRenderer.tsx       ← SVG Rasi chart renderer
│   │   ├── NavamsaRenderer.tsx     ← SVG Navamsa chart renderer
│   │   ├── PlanetTable.tsx         ← Tabular planet positions
│   │   ├── HouseTable.tsx          ← House cusp table
│   │   └── DashaTimeline.tsx       ← Visual Dasha timeline
│   ├── ai/
│   │   ├── AIChatConsole.tsx       ← AI question input + answer display
│   │   └── AnswerCard.tsx          ← Single Q&A display card
│   ├── compatibility/
│   │   ├── CompatibilityScoreCard.tsx
│   │   └── KutaScoreGrid.tsx
│   ├── credits/
│   │   ├── CreditBalanceWidget.tsx ← Top-nav credit display
│   │   └── CreditPackCard.tsx      ← Pricing card per pack
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   └── ui/                         ← shadcn/ui re-exports
├── lib/
│   ├── api/
│   │   ├── client.ts               ← Axios/fetch base client with auth headers
│   │   ├── auth.ts                 ← Auth API functions
│   │   ├── charts.ts               ← Charts API functions
│   │   ├── ai.ts                   ← AI API functions
│   │   ├── payments.ts             ← Payments API functions
│   │   └── compatibility.ts        ← Compatibility API functions
│   ├── store/
│   │   ├── authStore.ts            ← Zustand auth store
│   │   └── uiStore.ts              ← Zustand UI state store
│   ├── hooks/
│   │   ├── useAuth.ts              ← Auth hook
│   │   ├── useCharts.ts            ← React Query chart hooks
│   │   ├── useAI.ts                ← React Query AI hooks
│   │   └── useCredits.ts           ← React Query credit hooks
│   ├── types/
│   │   ├── chart.ts                ← Chart-related TypeScript types
│   │   ├── user.ts                 ← User types
│   │   ├── ai.ts                   ← AI Q&A types
│   │   └── payment.ts              ← Payment/credit types
│   └── utils/
│       ├── formatters.ts           ← Date, number, sign formatters
│       └── validators.ts           ← Form validation schemas (Zod)
├── public/
│   ├── fonts/
│   └── images/
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
└── .env.local
```

---

## 3. Pages Specification

---

### 3.1 Home Page (`/`)

**Type:** Public (SSG — Static Site Generation)

**Purpose:** Marketing landing page

**Sections:**
1. **Hero** — Headline, subtext, "Get Started Free" CTA, animated star/constellation background
2. **Features** — 4-column grid: Birth Chart, AI Insights, Compatibility, Predictions
3. **How It Works** — 3-step illustrated process
4. **Testimonials** — 3 user testimonial cards (static content)
5. **Pricing** — Credit pack cards with "Buy Now" buttons
6. **FAQ** — Accordion with 6–8 common questions
7. **Footer** — Links, social icons, copyright

**Components used:** `CreditPackCard`, `Footer`, `Navbar` (public variant)

---

### 3.2 Auth Pages (`/login`, `/register`)

**Type:** Public (client-side rendered)

**Login Fields:**
- Email (required, email format)
- Password (required, min 8 chars)
- "Remember me" toggle
- Forgot password link (future)
- Google OAuth button (future)

**Register Fields:**
- Full Name (required, 2–100 chars)
- Email (required, unique)
- Password (required, strong password)
- Confirm Password (must match)
- Terms of service checkbox (required)

**On Success:**
- Store `access_token` + `refresh_token` in `authStore` (Zustand)
- Store token in `httpOnly` cookie via backend Set-Cookie (preferred) OR `localStorage` (fallback)
- Redirect to `/dashboard`

---

### 3.3 Dashboard (`/dashboard`)

**Type:** Protected (requires auth)

**Sections:**
1. **Welcome Banner** — "Good morning, [Name]" with today's date and lunar day (Tithi)
2. **Credit Balance Widget** — Current credits, quick "Buy More" link
3. **Primary Chart Summary** — Ascendant, Sun, Moon; link to full chart
4. **Current Dasha** — Active Mahadasha + Antardasha with dates
5. **Quick Ask** — Single-line AI question input (shortcuts to `/ai` page)
6. **Recent Readings** — Last 3 AI answers (card list)
7. **Daily Forecast Card** — Today's AI daily prediction (auto-generated or prompt to generate)

---

### 3.4 New Birth Chart (`/charts/new`)

**Type:** Protected

**Form Fields:**

| Field | Input Type | Validation |
|---|---|---|
| Label | Text | Required, 2–100 chars |
| Person Name | Text | Required, 2–100 chars |
| Date of Birth | Date picker | Required, valid past date |
| Time of Birth | Time picker | Required unless "Time Unknown" checked |
| Time Unknown | Checkbox | If checked, TOB disabled |
| Place of Birth | Search with autocomplete | Required, geocoded |
| Is Primary Chart | Toggle | One primary chart per user |
| Ayanamsa | Select (Lahiri/Raman/KP) | Default: Lahiri |

**Place Autocomplete:** Debounced API call to geocoding endpoint as user types.

**On Submit:**
1. Validate all fields (Zod schema).
2. POST `/api/v1/charts`.
3. Show loading spinner.
4. On success: redirect to `/charts/{chartId}`.
5. On error: show inline error messages.

---

### 3.5 Chart Viewer (`/charts/[chartId]`)

**Type:** Protected

**Layout:** Two-column (chart SVG on left, details panel on right)

**Tabs:**
1. **Rasi Chart** — SVG chart rendered by `ChartRenderer`
2. **Navamsa Chart** — SVG chart rendered by `NavamsaRenderer`
3. **Planets** — `PlanetTable` component
4. **Houses** — `HouseTable` component
5. **Dashas** — `DashaTimeline` component
6. **Yogas** — Card list of detected yogas with descriptions

**Actions:**
- "Ask AI about this chart" → opens `AIChatConsole` pre-filled with chart ID
- "Delete Chart" → confirmation modal → DELETE `/api/v1/charts/{chartId}`

---

### 3.6 AI Question Console (`/ai`)

**Type:** Protected

**Layout:**
- Left panel: Chart selector dropdown + question type selector
- Center: `AIChatConsole` with conversation history style
- Right panel: Credit balance widget + recent questions

**Features:**
- Select chart from user's chart list (defaults to primary)
- Select question type: General / Daily / Weekly / Monthly / Full Reading
- Shows credit cost before submit: "This will use **1 credit** (Balance: 44)"
- Submit question → streaming or full response display
- Each answer shows: model used, tokens, date/time
- "Save to Readings" button (answers auto-saved; button marks as favourite)

**Credit Guard:** If balance = 0, show banner: "You're out of credits. [Buy More →]" and disable submit.

---

### 3.7 Saved Readings (`/ai/history`)

**Type:** Protected

**Layout:** Searchable, filterable list of past AI Q&A pairs.

**Filters:**
- By chart (dropdown)
- By question type
- By date range

**Each Card Shows:**
- Question text (truncated to 100 chars)
- Answer preview (first 150 chars)
- Date asked
- Credits used
- Expand button → full question + answer

---

### 3.8 Compatibility Checker (`/compatibility`)

**Type:** Protected

**Step 1:** Select user's own chart (defaults to primary)
**Step 2:** Select or add compatibility profile
**Step 3:** Select compatibility type: Love / Business / Friendship
**Step 4:** Enter optional question ("Will this partnership be successful?")
**Step 5:** Click "Check Compatibility" → shows 5-credit cost warning

**Results Display:**
- Overall compatibility score (0–100) with visual gauge
- Category scores (Emotional, Intellectual, Physical, Spiritual)
- Ashtakoot Kuta score grid (8 factors × score/max)
- AI narrative analysis (paragraphs)
- Strengths + Challenges sections

---

### 3.9 Pricing Page (`/payments`)

**Type:** Public (also accessible to logged-in users)

**Layout:** 3-column credit pack cards

**Each Card Shows:**
- Pack name + emoji
- Price (e.g., $9.99)
- Credit count
- Cost per credit
- Feature list (what you can do with these credits)
- CTA button: "Buy Now" → POST checkout

**If not logged in:** "Buy Now" redirects to `/register`

---

### 3.10 User Profile (`/profile`)

**Type:** Protected

**Sections:**
- Name and email display (with edit name option)
- Change password form
- Credit usage summary
- Account deletion (future phase)

---

## 4. Component Specifications

---

### 4.1 `ChartRenderer` (SVG)

**Props:**
```typescript
interface ChartRendererProps {
  chartJson: ChartJson;
  style: "north_indian" | "south_indian" | "east_indian";
  size?: number;         // SVG size in px (default: 400)
  showLabels?: boolean;
  highlightPlanet?: string;
}
```

**North Indian Style:** Diamond grid layout — 12 rhombus houses
**South Indian Style:** Fixed square grid — 12 squares in a 4×4 grid with corners removed

**Rendering Logic:**
1. Draw grid based on selected style (SVG paths).
2. Assign each sign to its house box.
3. Render planet glyphs (Unicode symbols or custom SVG glyphs) in their respective house boxes.
4. Render ascendant marker.
5. Optional: hover tooltip on planet symbol showing full planet details.

---

### 4.2 `PlanetTable`

**Props:**
```typescript
interface PlanetTableProps {
  planets: PlanetPosition[];
  showExtended?: boolean;  // Include combustion, dignity
}
```

**Columns:** Planet | Sign | House | Degree | Nakshatra | Pada | Retrograde | Dignity

---

### 4.3 `DashaTimeline`

**Props:**
```typescript
interface DashaTimelineProps {
  dashas: DashaData;
  showAntarDashas?: boolean;
}
```

**Rendering:** Horizontal timeline bar; Mahadasha = large segment, Antardasha = subdivisions; current period highlighted with a marker.

---

### 4.4 `AIChatConsole`

**Props:**
```typescript
interface AIChatConsoleProps {
  chartId: string;
  questionType?: QuestionType;
  initialQuestion?: string;
}
```

**Features:**
- Textarea input (max 500 chars, with char counter)
- Submit button with spinner during API call
- Answer rendered as formatted Markdown (using `react-markdown`)
- Shows model, tokens, credits used below each answer
- "Copy answer" button

---

### 4.5 `CreditBalanceWidget`

**Props:**
```typescript
interface CreditBalanceWidgetProps {
  variant: "navbar" | "sidebar" | "full";
}
```

**`navbar` variant:** Small pill showing credit count + icon (e.g., ✦ 44)
**`sidebar` variant:** Medium card with balance + "Buy More" link
**`full` variant:** Full card with balance, total purchased, total used, recent history

---

### 4.6 `CompatibilityScoreCard`

**Props:**
```typescript
interface CompatibilityScoreCardProps {
  result: CompatibilityResult;
}
```

**Displays:** Circular gauge (0–100), category scores as horizontal bars, Kuta grid table.

---

## 5. State Management

### 5.1 Zustand — `authStore`

```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  creditBalance: number;
  isAuthenticated: boolean;
  
  setUser: (user: User) => void;
  setAccessToken: (token: string) => void;
  setCreditBalance: (balance: number) => void;
  logout: () => void;
}
```

### 5.2 Zustand — `uiStore`

```typescript
interface UIState {
  sidebarOpen: boolean;
  activeChartId: string | null;
  
  toggleSidebar: () => void;
  setActiveChart: (id: string | null) => void;
}
```

### 5.3 React Query — Key Patterns

```typescript
// Chart queries
queryKey: ["charts"]                           // list
queryKey: ["charts", chartId]                  // single chart
queryKey: ["ai-history", { chartId, page }]    // AI history
queryKey: ["credits"]                          // credit balance
queryKey: ["compatibility-profiles"]           // profiles list

// Mutations
mutationFn: createChart
mutationFn: askAIQuestion       // invalidates ["ai-history", "credits"]
mutationFn: createCheckout
```

---

## 6. API Client (`lib/api/client.ts`)

```typescript
// Base Axios/fetch client
// - Automatically attaches Authorization: Bearer <token> header
// - Intercepts 401 → attempts token refresh → retries request
// - Intercepts 402 → triggers credit-low UI state
// - Intercepts 429 → shows rate limit toast
// - All requests include X-Request-ID header (UUID)
```

---

## 7. Authentication Flow (Frontend)

1. On app load: read `access_token` from store/cookie.
2. If present: validate by calling `GET /auth/me`. On success, populate `authStore`.
3. If `GET /auth/me` returns `401`: attempt refresh → if refresh fails, redirect to `/login`.
4. All protected routes wrapped in middleware (`middleware.ts`) that checks auth state.
5. Next.js middleware redirects unauthenticated users to `/login?redirect=<original_path>`.
6. After login: redirect back to original path from query param.

---

## 8. Design System

**Typography:**
- Headings: `Cormorant Garamond` (serif — elegant, traditional feel)
- Body: `Inter` (clean sans-serif)
- Code/data: `JetBrains Mono`

**Color Palette (TailwindCSS custom tokens):**

| Token | Value | Usage |
|---|---|---|
| `primary` | Indigo #4F46E5 | Buttons, links, active states |
| `primary-dark` | #3730A3 | Hover states |
| `gold` | #D4AF37 | Auspicious accents, stars |
| `surface` | #0F0F1A | Dark background |
| `surface-card` | #1A1A2E | Card backgrounds |
| `surface-border` | #2A2A3E | Borders |
| `text-primary` | #F0EFE8 | Main text (cream/off-white) |
| `text-muted` | #8B8BA7 | Secondary text |
| `success` | #10B981 | Positive indicators |
| `warning` | #F59E0B | Caution states |
| `error` | #EF4444 | Error states |

**Theme:** Dark mode first (matches astrology/mystical aesthetic). Light mode in Phase 2.

---

## 9. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| FE1 | Chart style default | North Indian / South Indian / User preference | 🟡 Pending |
| FE2 | Token storage | httpOnly cookie / localStorage / Zustand only | 🟡 Pending |
| FE3 | AI response streaming | Yes (SSE) / No (batch) | 🟡 Pending |
| FE4 | Chart SVG library | Custom SVG / react-konva / d3.js | 🟡 Pending |
| FE5 | Light mode | Phase 1 / Phase 2 | 🟡 Pending |
| FE6 | PWA support | Phase 1 / Phase 2 | 🟡 Pending |
| FE7 | Markdown renderer for AI answers | react-markdown / custom | 🟡 Pending |

---

*This document is a living specification. Sections marked 🟡 are pending decisions.*
