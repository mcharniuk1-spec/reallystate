# Product UX Structure — LUN-Style Buyer-Oriented Marketplace

## 1. Platform Identity

**Name:** (TBD — working title: "BG Property Scout")  
**Tagline:** "Every property. One search. 3D map."  
**Model:** Buyer-oriented marketplace. Owners post directly. Agents appear as "owner representative" (never labeled "realtor").

### Core Principles

1. **Buyer-first:** Every UX decision optimizes the buyer/renter search experience
2. **Owner-posts:** Property owners are the primary posters; agents manage on behalf of owners
3. **Complete supply:** Aggregation means seeing 95%+ of available properties in one place
4. **Map-driven:** The map is not a feature — it IS the product (LUN.ua model)
5. **AI-native:** Chat assistant is always present, always aware of context

---

## 2. Information Architecture

```
/                        → Homepage (map + feed split view)
/listings                → Full listings feed with filters
/properties/[id]         → Property detail page
/map                     → Full-screen 3D map
/chat                    → AI chat (also persistent sidebar everywhere)
/new-builds              → Developer projects catalog
/analytics               → Market analytics (STR yields, price trends)
/settings                → User profile, saved searches, alerts
/admin                   → Operator dashboard (internal)
/post                    → Owner listing submission
```

---

## 3. Page Specifications

### 3.1 Homepage — Split View (Main Experience)

**Layout:** Map (left 55%) + Listing Feed (right 45%)  
**Mobile:** Stacks vertically — feed on top, map below (swipeable)

```
┌─────────────────────────────────────┬──────────────────────────┐
│                                     │ ┌──────────────────────┐ │
│           3D MAP (Varna)            │ │  Intent Toggle       │ │
│                                     │ │  [Buy][Rent][STR]    │ │
│    ┌─────────┐                      │ ├──────────────────────┤ │
│    │ Building │                      │ │  Category Picker     │ │
│    │  hover   │                      │ │  Apt House Villa Land│ │
│    └─────────┘                      │ ├──────────────────────┤ │
│                                     │ │  Search Bar + Filters│ │
│         ● ● ●                       │ ├──────────────────────┤ │
│        Property pins                │ │  ┌──────────────────┐│ │
│                                     │ │  │  Listing Card    ││ │
│                                     │ │  │  Photo | Price   ││ │
│                                     │ │  │  Area | Rooms    ││ │
│                                     │ │  │  Source badge     ││ │
│                                     │ │  └──────────────────┘│ │
│    [2D/3D] [Layers] [Draw]         │ │  ┌──────────────────┐│ │
│                                     │ │  │  Listing Card    ││ │
│                                     │ │  │  ...             ││ │
│                                     │ │  └──────────────────┘│ │
│                                     │ │  ∞ infinite scroll   │ │
├─────────────────────────────────────┤ └──────────────────────┘ │
│ [AI Chat] persistent bottom bar     │                          │
└─────────────────────────────────────┴──────────────────────────┘
```

**Interactions:**
- Hover card → highlight pin on map
- Click pin → scroll to card + expand preview
- Drag map → filter feed to visible area
- Draw polygon → filter to custom area
- Zoom to building → show building summary drawer
- 2D/3D toggle → switch between flat and extruded view

### 3.2 Listing Card

```
┌─────────────────────────────────────┐
│ ┌──────────┐  €85,000  ●→ Buy      │
│ │          │  Varna, Chaika dist.   │
│ │  Photo   │  2 rooms · 68 m²      │
│ │  gallery │  Floor 4/8 · 2019     │
│ │  (swipe) │                        │
│ └──────────┘  [imot.bg] [Homes.bg]  │
│  Updated: 2 hours ago    ♥ Save     │
└─────────────────────────────────────┘
```

**Key elements:**
- Photo carousel (swipeable, 3–5 photos visible)
- Price prominently displayed with price/m² below
- Source badges (which portals list this property)
- Freshness indicator (how recently updated)
- Save/favorite action
- NO "agent" label — if listed by agent, shows "Owner representative: [Name]"

### 3.3 Property Detail Page — `/properties/[id]`

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to results                                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Photo Gallery (fullscreen capable)     │    │
│  │   ◄  [1] [2] [3] [4] [5] [6] ... ►                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────┐  ┌─────────────────────────────────┐    │
│  │  €85,000       │  │  Facts Grid                     │    │
│  │  €1,250/m²     │  │  Type: Apartment                │    │
│  │                │  │  Rooms: 2                        │    │
│  │  Price History │  │  Area: 68 m²                     │    │
│  │  [chart]       │  │  Floor: 4 of 8                   │    │
│  │                │  │  Year: 2019                       │    │
│  │  Contact:      │  │  Construction: Brick             │    │
│  │  Owner repr.   │  │  Act 16: Yes                     │    │
│  │  [Phone] [Msg] │  │  Amenities: Parking, Balcony     │    │
│  └────────────────┘  └─────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Description (expandable)                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Mini Map (location + nearby properties)             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Source Links (listed on: imot.bg, Homes.bg, alo.bg)│    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Similar Properties (3–6 cards)                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [AI Chat: "Ask about this property"]                       │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 AI Chat Panel

**Persistent sidebar** (right side on desktop, bottom sheet on mobile). Always visible. Always aware of:
- Currently selected/viewed property
- Active search filters (area, price range, type)
- Map viewport (what's visible on screen)
- User's saved searches and history

**Capabilities:**
- "Show me 2-bedroom apartments under €90K in Chaika" → filters map + feed
- "Compare this property with the one I saved yesterday" → side-by-side
- "What's the price trend in this district?" → analytics chart
- "Is this a good investment? Show STR yield" → AirDNA/Airbtics data
- "Find similar but with sea view" → refined search
- "Contact the owner" → opens message/call

### 3.5 Full-Screen Map — `/map`

Same map as homepage but full-screen with overlay panels:
- Floating filter bar at top
- Building summary drawer (slides in from right)
- Cluster markers at low zoom → individual pins at high zoom
- 3D building extrusion with property data on click
- Layer controls: satellite, terrain, buildings, heatmap (price/density)

### 3.6 New Builds Catalog — `/new-builds`

**LUN.ua-inspired construction tracking:**
- Developer profile cards
- Project cards with completion status, floor plans, pricing
- Construction progress timeline (if photos available)
- Unit availability matrix (floor × unit type)
- Developer reliability rating

### 3.7 Owner Listing Submission — `/post`

Simple wizard for property owners:
1. Property type + intent (sell/rent)
2. Location (address + pin on map)
3. Details (area, rooms, floor, year, amenities)
4. Photos (upload 5–20)
5. Price + description
6. Contact method (phone, chat, email)
7. Optional: assign representative (agent) to manage

---

## 4. Component Tree

```
App
├── Layout
│   ├── Header (logo, nav, search, user menu)
│   ├── AIChat (persistent sidebar/bottom sheet)
│   └── Footer
│
├── HomePage (/)
│   ├── IntentToggle (Buy/Rent/STR/Auction/Land)
│   ├── CategoryPicker (Apartment/House/Villa/Studio/Commercial/Land)
│   ├── SearchBar (text + location autocomplete)
│   ├── FilterPanel (price, area, rooms, floor, year, amenities)
│   ├── MapCanvas (MapLibre + deck.gl)
│   │   ├── BuildingLayer (3D extrusion)
│   │   ├── PropertyPinLayer
│   │   ├── ClusterLayer
│   │   ├── DrawToolLayer (polygon selection)
│   │   └── MapControls (2D/3D, layers, zoom)
│   └── ListingFeed
│       ├── ListingCard (× n)
│       │   ├── PhotoCarousel
│       │   ├── PriceDisplay
│       │   ├── SourceBadges
│       │   └── FreshnessBadge
│       └── InfiniteScrollLoader
│
├── PropertyDetail (/properties/[id])
│   ├── PhotoGallery (fullscreen, swipe, zoom)
│   ├── PriceBox (price, price/m², price history chart)
│   ├── FactsGrid
│   ├── DescriptionTabs (full text, machine translation)
│   ├── ContactPanel (owner/representative info)
│   ├── MapMiniPanel (location + nearby)
│   ├── SourceLinksPanel
│   ├── SimilarProperties
│   └── AIChat (contextualized to this property)
│
├── FullScreenMap (/map)
│   ├── MapCanvas (full viewport)
│   ├── FloatingFilterBar
│   ├── BuildingSummaryDrawer
│   └── ListingPreviewCard (on pin click)
│
├── NewBuilds (/new-builds)
│   ├── DeveloperList
│   ├── ProjectCard
│   ├── UnitMatrix
│   └── ProgressTimeline
│
├── Analytics (/analytics)
│   ├── PriceTrendChart
│   ├── YieldCalculator
│   ├── DistrictComparison
│   └── STRMetrics
│
├── PostListing (/post)
│   ├── PropertyTypeStep
│   ├── LocationStep (map pin)
│   ├── DetailsStep
│   ├── PhotoUploadStep
│   ├── PricingStep
│   └── ReviewSubmitStep
│
├── Settings (/settings)
│   ├── ProfileSettings
│   ├── SavedSearches
│   ├── AlertPreferences
│   └── AccountSettings
│
└── Admin (/admin)
    ├── SourceHealthDashboard
    ├── CrawlerJobTable
    ├── ParserFailureQueue
    ├── DuplicateReviewQueue
    └── PublishQueue
```

---

## 5. Mobile Responsive Strategy

| Breakpoint | Layout |
|---|---|
| Desktop (>1200px) | Map left 55% + Feed right 45% |
| Tablet (768–1200px) | Map left 45% + Feed right 55% |
| Mobile (<768px) | Feed on top (scrollable) + Map below (expandable) + Bottom sheet chat |

Mobile-specific:
- Swipe between map and feed views
- Bottom sheet for AI chat
- Pull-to-refresh listing feed
- Floating "Map" / "List" toggle button
- Photo gallery becomes fullscreen swipe

---

## 6. Design System Tokens (Planned)

| Token | Value | Usage |
|---|---|---|
| `--brand-primary` | #4361ee | Buttons, links, map pins |
| `--brand-accent` | #e94560 | Price highlights, alerts, CTAs |
| `--brand-success` | #16c79a | Verified, new, available |
| `--brand-warning` | #f9c74f | Expiring, needs review |
| `--brand-dark` | #1a1a2e | Text, headers |
| `--brand-light` | #f5f5f5 | Backgrounds, cards |
| `--font-sans` | Inter, system-ui | Body text |
| `--font-mono` | JetBrains Mono | Prices, IDs, code |
| `--radius-card` | 12px | Card corners |
| `--radius-button` | 8px | Button corners |
| `--shadow-card` | 0 2px 8px rgba(0,0,0,0.08) | Card elevation |

---

## 7. Reference Platforms

| Platform | What to copy | What to improve |
|---|---|---|
| LUN.ua | Map + feed split, construction tracking, AI dedupe | Add AI chat, 3D buildings, cross-source transparency |
| Rightmove (UK) | Saved searches, email alerts, "draw a search" on map | Add price history, source badges, STR analytics |
| Idealista (Spain) | Mobile-first design, international buyer funnel | Add owner-first posting, agent-as-representative model |
| Zillow (US) | Zestimate price prediction, "Make me move" | Adapt yield calculator for BG market |
| Hemnet (Sweden) | Premium placement model, transparent pricing | Adapt to BG agency ecosystem |
