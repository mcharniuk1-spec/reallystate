# Refined Product UX Structure — LUN-Style Buyer Marketplace

**Slice**: UX-06  
**Status**: `DONE_AWAITING_VERIFY`  
**Date**: 2026-04-08  
**Author**: ux_ui_designer agent  
**Input docs**: `docs/business/product-ux-structure.md`, `docs/business/unit-economics-market-analysis.md`, `PLAN.md` §8

---

## 1. Platform identity

**Name**: BGEstate (working title)  
**Tagline**: "Every property. One search. 3D map."  
**Model**: buyer-oriented marketplace; owners post directly; agents appear only as "owner representative"

---

## 2. Design system (refined from existing Tailwind tokens)

The current codebase uses a warm paper/sea palette. The product UX structure doc proposed a blue/red brand system. This refinement keeps the existing tokens (already in code) and adds missing ones.

### Color tokens (preserving `tailwind.config.ts`)

| Token | Value | Usage |
|---|---|---|
| `ink` | #0f1419 | Body text, headers |
| `mist` | #64748b | Secondary text, metadata |
| `paper` | #f6f3ed | Page backgrounds |
| `panel` | #fffcf7 | Card backgrounds |
| `line` | #e5dfd3 | Borders, dividers |
| `sea` | #0b6b57 | Primary brand (buttons, links, map pins) |
| `sea-bright` | #0d8a72 | Primary hover/active |
| `sand` | #c9a962 | Accent (price highlights, badges) |
| `warn` | #b45309 | Alerts, errors, expiring |
| `purple-soft` | #7c3aed | Rent intent badge |
| `rose` | #e11d48 | CTA accent (save, featured) |

### Typography (preserving `next/font/google`)

| Token | Font | Usage |
|---|---|---|
| `font-sans` | Outfit | UI text, buttons, navigation, metadata |
| `font-display` | Newsreader | Prices, headings, property titles |
| `font-mono` | system monospace | IDs, external IDs, debug info |

### Spacing and radii

| Token | Value |
|---|---|
| `radius-card` | `rounded-2xl` (16px) |
| `radius-button` | `rounded-full` (pill) for primary; `rounded-xl` (12px) for secondary |
| `radius-input` | `rounded-xl` (12px) |
| `shadow-card` | `shadow-lift` (0 18px 50px rgb(15 20 25 / 8%)) |

---

## 3. Route map (all pages)

```
/                        → Homepage: map + listing feed split view (built)
/properties/[id]         → Property detail page (built, needs enrichment)
/map                     → Full-screen 3D map (built, needs building layer)
/chat                    → AI chat full view (shell exists)
/new-builds              → Developer projects catalog (new)
/analytics               → Market analytics: price trends, STR yields (new)
/post                    → Owner listing submission wizard (new)
/settings                → User profile, saved searches, alerts (shell exists)
/admin                   → Operator dashboard (spec done, shell exists)
/auth/login              → Login page (new)
/auth/register           → Registration page (new)
```

---

## 4. Page-by-page wireframe specs

### 4.1 Homepage `/` — Split view (CURRENT: built in UX-02/03)

```
┌────────────────────────────────────────────────────────────────────────┐
│ [Logo]  [Browse●]  [Full map]  [Chat]  [Admin]        [Beta] [●User] │
├────────────────────────────────────────────────────────────────────────┤
│ [All][Buy][Rent][Short-term][Auction]  🔍 Search city...   12 results │
│ [All types][Apartment][House][Studio][Villa][Penthouse][Office][Land]  │
├──────────────────────────────────┬─────────────────────────────────────┤
│                                  │ ┌─────────────────────────────────┐ │
│          MapLibre GL JS          │ │ [Photo area]         For sale  │ │
│     (Bulgaria / Varna scope)     │ │ €185,000                       │ │
│                                  │ │ Lozenets, Sofia                │ │
│    ● ● ●  property pins         │ │ Apartment · 92m² · 3 rooms     │ │
│    hover ↔ card highlight        │ │ Homes.bg              2h ago   │ │
│                                  │ ├─────────────────────────────────┤ │
│    [2D/3D] [Layers]             │ │ [Photo area]         For rent  │ │
│                                  │ │ €450/mo                        │ │
│                                  │ │ Sea Garden, Varna              │ │
│                                  │ │ Studio · 38m²                  │ │
│                                  │ ├─────────────────────────────────┤ │
│                                  │ │         ∞ scroll               │ │
├──────────────────────────────────┴─────────────────────────────────────┤
│  [AI Chat: "Find me a 2-bed in Varna under €90K"]      persistent bar│
└────────────────────────────────────────────────────────────────────────┘
```

**Status**: Built (UX-02/03). Needs advanced filters (UX-08), 3D buildings (UX-07), and AI chat bar (UX-05).

**Refinements for UX-08**:
- Add collapsible filter sidebar: price range, area range, rooms, floor, year, construction, amenities, source filter, sort
- Add map-to-feed sync: drag map → filter feed to visible area
- Add polygon draw tool → filter to custom area
- Add loading skeleton (shimmer cards)

---

### 4.2 Listing card (CURRENT: built in UX-02)

```
┌─────────────────────────────────────────────────┐
│ ┌──────────────┐  €85,000          ● For sale  │
│ │ Photo        │  €1,250/m²                     │
│ │ carousel     │  Varna, Chaika                  │
│ │ (swipe)      │  2 rooms · 68 m² · Floor 4/8   │
│ └──────────────┘                                 │
│ [imot.bg] [Homes.bg]   Updated 2h ago    ♥ Save │
└─────────────────────────────────────────────────┘
```

**Refinements for UX-08**:
- Photo carousel (3–5 images, swipe on mobile, arrow keys on desktop)
- Price/m² below price
- Floor info when available
- Save/favorite button (disabled until auth, UX-10)
- "Owner representative" label instead of agent label

---

### 4.3 Property detail `/properties/[id]` (CURRENT: built in UX-03)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] / Varna / Chaika / 2-bed apartment        [← Back]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │           Photo Gallery (fullscreen, swipe, zoom)           │ │
│ │    ◄  [1]  [2]  [3]  [4]  [5]  ►     📷 12 photos         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌──────────────────────┐  ┌────────────────────────────────┐   │
│ │ €85,000              │  │ Type: Apartment                │   │
│ │ €1,250/m²            │  │ Rooms: 2                       │   │
│ │                      │  │ Area: 68 m²                    │   │
│ │ Price history [chart]│  │ Floor: 4 of 8                  │   │
│ │                      │  │ Year: 2019 · Brick             │   │
│ │ Contact:             │  │ Act 16: Yes                    │   │
│ │ Owner representative │  │ Parking, Balcony, Elevator     │   │
│ │ [📞 Call] [💬 Msg]   │  │                                │   │
│ └──────────────────────┘  └────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Description (expandable, BG ↔ EN toggle)                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Mini Map (property pin + 3-5 nearby properties)             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Listed on: [imot.bg ↗] [Homes.bg ↗] [alo.bg ↗] + dates    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Similar properties (3-6 cards, same district + price band)  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [AI: "Ask about this property"]                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Status**: Basic layout built (UX-03). Missing: photo gallery, price history chart, contact panel, mini map, source links, similar properties, breadcrumb, share, save. All deferred to UX-09.

---

### 4.4 Full-screen map `/map` (CURRENT: built in UX-02)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo]  Full map view                              [← Listings] │
├─────────────────────────────────────────────────────────────────┤
│ ┌─── Floating filter bar ───────────────────────────────────┐   │
│ │ [Buy][Rent][STR]  [Apt][House][Villa]  Price ▼  Rooms ▼   │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    Full viewport MapLibre                        │
│                                                                 │
│     ● ● ● ●    Clusters at low zoom                            │
│     ●        →  Individual pins at high zoom                    │
│     █████       3D building extrusion (Varna)                   │
│                                                                 │
│                 ┌────────────────────────┐                      │
│                 │ Building Summary Drawer │ ← slides in on click│
│                 │ 4 listings in building  │                      │
│                 │ Price range: €65–95K    │                      │
│                 │ [View all →]            │                      │
│                 └────────────────────────┘                      │
│                                                                 │
│ [2D/3D] [Satellite] [Heatmap] [Draw polygon]                   │
│                                                                 │
│ [AI Chat] persistent bar                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Status**: Basic full-screen map built. Missing: floating filters, building layer, building drawer, cluster markers, layer controls, heatmap. Deferred to UX-07 (3D buildings) + UX-08 (filters).

---

### 4.5 AI chat `/chat` (CURRENT: shell exists)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo]  [Browse]  [Map]  [Chat●]  [Admin]          [User]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─── Chat thread ───────────────────────────────────────────┐   │
│ │                                                           │   │
│ │ 🤖 Welcome! I can help you find properties in Bulgaria.   │   │
│ │    Tell me what you're looking for.                        │   │
│ │                                                           │   │
│ │ 👤 Show me 2-bed apartments in Varna under €90K           │   │
│ │                                                           │   │
│ │ 🤖 Found 23 apartments matching your criteria.             │   │
│ │    [Map view: Varna filtered]                              │   │
│ │    [Top 3 listing cards inline]                            │   │
│ │    Price range: €65K–€89K                                  │   │
│ │    Most popular district: Chaika (8 listings)             │   │
│ │    Want me to narrow by district or amenities?             │   │
│ │                                                           │   │
│ │ 👤 What's the STR yield in Chaika?                         │   │
│ │                                                           │   │
│ │ 🤖 Chaika avg STR yield: 4.2% gross                       │   │
│ │    ADR: €58/night, Occupancy: 61%                          │   │
│ │    [Source: AirDNA licensed data]                           │   │
│ │                                                           │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ 💬 Ask about properties, prices, neighborhoods...    [→]  │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Context awareness**: the chat knows the currently viewed property, active filters, map viewport, user's saved searches, and can push actions (filter map, open property, compare).

**Status**: Shell page exists. Implementation blocked on UX-05 (depends on UX-04, BD-07).

---

### 4.6 New builds `/new-builds` (NOT YET STARTED)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo]  [Browse]  [Map]  [New Builds●]  [Chat]      [User]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Developer projects in Varna (and coastal Bulgaria)              │
│                                                                 │
│ ┌──────────────────────┐ ┌──────────────────────┐              │
│ │ [Rendering photo]    │ │ [Rendering photo]    │              │
│ │ Marina Bay Residence │ │ Sunrise Park Tower   │              │
│ │ by Trace Group BG    │ │ by Shining Star Ltd  │              │
│ │ Status: Construction │ │ Status: Act 16 ready │              │
│ │ From €1,450/m²       │ │ From €1,800/m²       │              │
│ │ 156 units · Q2 2027  │ │ 44 units · Ready     │              │
│ │ [View project →]     │ │ [View project →]     │              │
│ └──────────────────────┘ └──────────────────────┘              │
│                                                                 │
│ ┌─ Project detail (expanded) ───────────────────────────────┐   │
│ │ Floor plan matrix: 1-bed / 2-bed / 3-bed per floor        │   │
│ │ Construction timeline with photos                          │   │
│ │ Unit availability: ██░░ 62% sold                          │   │
│ │ Developer profile + past projects                          │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Blocked**: no backend task defined yet. Add as future UX slice after core flows stabilize.

---

### 4.7 Analytics `/analytics` (NOT YET STARTED)

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo]  [Browse]  [Map]  [Analytics●]  [Chat]       [User]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Market overview: Varna                                          │
│                                                                 │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐       │
│ │ Avg price/m²   │ │ Active listings│ │ Avg days to    │       │
│ │ €1,900         │ │ 4,200          │ │ sell: 45       │       │
│ │ +17% YoY       │ │ -3% vs Q1      │ │ -8% vs Q1     │       │
│ └────────────────┘ └────────────────┘ └────────────────┘       │
│                                                                 │
│ ┌─── Price trend chart (12mo) ──────────────────────────────┐   │
│ │ [Line chart: price/m² by district over time]               │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─── STR yield calculator ──────────────────────────────────┐   │
│ │ Property price: [€85,000]  Annual revenue: [€14,200]       │   │
│ │ Gross yield: 16.7%   Net yield: ~11% (after expenses)      │   │
│ │ Occupancy assumption: 59%   ADR: €65                       │   │
│ │ [Source: AirDNA/Airbtics licensed data]                    │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─── District comparison ───────────────────────────────────┐   │
│ │ [Bar chart: avg price/m² by district]                      │   │
│ └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**Blocked**: depends on STR analytics backend (T3-08) and price aggregation (BD-03+).

---

### 4.8 Post listing `/post` (NOT YET STARTED — seller mode)

```
Step 1: Intent        [Sell] [Rent] [Short-term rental]
Step 2: Category      [Apartment] [House] [Villa] [Land] [Other]
Step 3: Location      [Address input + pin on map]
Step 4: Details       [Area] [Rooms] [Floor/Total] [Year] [Construction]
                      [Amenities checkboxes]
Step 5: Photos        [Upload 5-20, drag to reorder, crop]
Step 6: Price         [Amount] [Currency EUR/BGN] [Description BG/EN]
Step 7: Contact       [Phone] [Chat only] [Email]
Step 8: Review        [Preview card + submit]
```

**Blocked**: depends on BD-13 (user auth + listing submission API).

---

### 4.9 Auth pages `/auth/login`, `/auth/register` (NOT YET STARTED)

```
┌─────────────────────────────────────────┐
│           BGEstate                       │
│                                         │
│   Create your account                    │
│                                         │
│   Name     [______________]              │
│   Email    [______________]              │
│   Password [______________]              │
│                                         │
│   I want to:                             │
│   (●) Browse & buy/rent                  │
│   ( ) List my property for sale/rent     │
│                                         │
│   [Create account]                       │
│                                         │
│   Already have an account? [Log in →]    │
└─────────────────────────────────────────┘
```

**Blocked**: depends on BD-13 (auth API).

---

### 4.10 Settings `/settings` (CURRENT: shell exists)

Sections:
1. **Profile**: name, email, phone, avatar, preferred language (BG/EN), mode switch
2. **Saved properties**: grid of favorited listings with remove action
3. **Saved searches**: filter combos with alert toggle (email/push frequency)
4. **Notifications**: email alerts, push preferences, SMS opt-in
5. **Account**: change password, delete account, export data

**Blocked**: depends on BD-13 (auth API) + UX-10.

---

## 5. Complete component tree

```
App
├── RootLayout
│   ├── Providers (TanStack Query)
│   └── Fonts (Outfit, Newsreader)
│
├── HomePage (/)                                      [BUILT]
│   ├── CompactHeader                                 [BUILT]
│   ├── FilterBar                                     [BUILT, needs expansion]
│   │   ├── IntentToggle                              [BUILT]
│   │   ├── CategoryPicker                            [BUILT]
│   │   ├── SearchInput                               [BUILT]
│   │   ├── PriceRangeSlider                          [UX-08]
│   │   ├── AreaRangeSlider                           [UX-08]
│   │   ├── RoomsDropdown                             [UX-08]
│   │   ├── FloorRange                                [UX-08]
│   │   ├── AmenitiesCheckboxes                       [UX-08]
│   │   ├── SourceFilter                              [UX-08]
│   │   └── SortSelector                              [UX-08]
│   ├── MapCanvas                                     [BUILT]
│   │   ├── PropertyPinLayer                          [BUILT]
│   │   ├── ClusterLayer                              [UX-07]
│   │   ├── BuildingLayer (3D extrusion)              [UX-07]
│   │   ├── DrawToolLayer (polygon selection)         [UX-08]
│   │   └── MapControls (2D/3D, layers)               [UX-07]
│   ├── ListingFeed                                   [BUILT]
│   │   ├── ListingCard (× n)                         [BUILT, needs photo carousel]
│   │   │   ├── PhotoCarousel                         [UX-08]
│   │   │   ├── PriceDisplay (price + price/m²)       [BUILT]
│   │   │   ├── IntentBadge                           [BUILT]
│   │   │   ├── FactsRow                              [BUILT]
│   │   │   ├── SourceBadges                          [BUILT, needs multi-source]
│   │   │   ├── FreshnessBadge                        [BUILT]
│   │   │   └── SaveButton                            [UX-10]
│   │   └── InfiniteScrollSentinel                    [BUILT]
│   └── AIChatBar (persistent bottom)                 [UX-05]
│
├── PropertyDetail (/properties/[id])                 [BUILT, needs enrichment]
│   ├── Breadcrumb                                    [UX-09]
│   ├── PhotoGallery (fullscreen, swipe, zoom)        [UX-09]
│   ├── PriceBox (price, price/m², history chart)     [BUILT basic, chart UX-09]
│   ├── FactsGrid                                     [BUILT]
│   ├── DescriptionPanel (expandable, BG↔EN)          [BUILT basic, translate UX-09]
│   ├── ContactPanel                                  [UX-09]
│   ├── MapMiniPanel (location + nearby)              [UX-09]
│   ├── SourceLinksPanel                              [BUILT]
│   ├── SimilarProperties (3-6 cards)                 [UX-09]
│   ├── ShareButton                                   [UX-09]
│   ├── SaveButton                                    [UX-10]
│   └── AIChatContext                                 [UX-05]
│
├── FullScreenMap (/map)                              [BUILT basic]
│   ├── FloatingFilterBar                             [UX-07]
│   ├── MapCanvas (full viewport + 3D)                [BUILT, 3D UX-07]
│   ├── BuildingSummaryDrawer                         [UX-07]
│   └── ListingPreviewCard                            [UX-07]
│
├── ChatPage (/chat)                                  [SHELL]
│   ├── ChatThread                                    [UX-05]
│   ├── MessageComposer                               [UX-05]
│   └── ContextPanel (current filters/property)       [UX-05]
│
├── NewBuilds (/new-builds)                           [NOT STARTED]
│   ├── ProjectGrid                                   [future]
│   ├── ProjectCard                                   [future]
│   ├── UnitMatrix                                    [future]
│   └── ProgressTimeline                              [future]
│
├── Analytics (/analytics)                            [NOT STARTED]
│   ├── MarketOverviewCards                            [future]
│   ├── PriceTrendChart                               [future]
│   ├── YieldCalculator                               [future]
│   └── DistrictComparison                            [future]
│
├── PostListing (/post)                               [NOT STARTED]
│   ├── IntentStep                                    [UX-10]
│   ├── CategoryStep                                  [UX-10]
│   ├── LocationStep (address + map pin)              [UX-10]
│   ├── DetailsStep                                   [UX-10]
│   ├── PhotoUploadStep                               [UX-10]
│   ├── PricingStep                                   [UX-10]
│   ├── ContactStep                                   [UX-10]
│   └── ReviewSubmitStep                              [UX-10]
│
├── Auth (/auth/*)                                    [NOT STARTED]
│   ├── LoginPage                                     [UX-10]
│   ├── RegisterPage                                  [UX-10]
│   └── AuthGuard (HOC)                               [UX-10]
│
├── Settings (/settings)                              [SHELL]
│   ├── ProfileSettings                               [UX-10]
│   ├── SavedProperties                               [UX-10]
│   ├── SavedSearches                                 [UX-10]
│   ├── AlertPreferences                              [UX-10]
│   └── AccountSettings                               [UX-10]
│
├── Admin (/admin)                                    [SHELL + SPEC]
│   ├── SystemHealthStrip                             [spec in UX-01]
│   ├── AdminKpiRow                                   [spec in UX-01]
│   ├── AdminQueueSidebar                             [spec in UX-01]
│   └── QueuePanels (7 panels)                        [spec in UX-01]
│
└── Shared components
    ├── AppShell                                      [BUILT]
    ├── LiveBackendPill                               [BUILT]
    ├── CoverageBar                                   [spec in UX-01]
    ├── StatusBadge                                   [spec in UX-01]
    ├── TierBadge                                     [spec in UX-01]
    ├── MetadataDrawer                                [spec in UX-01]
    └── EmptyStateCard                                [spec in UX-01]
```

---

## 6. Mobile responsive strategy

| Breakpoint | Layout |
|---|---|
| Desktop (>1200px) | Map left 55–60% + Feed right 40–45% |
| Tablet (768–1200px) | Map left 45% + Feed right 55% |
| Mobile (<768px) | Stacked: filter bar → listing feed → expandable map |

### Mobile-specific patterns

| Pattern | Implementation |
|---|---|
| Map/List toggle | Floating FAB button at bottom-right: tap to switch between map and feed |
| AI chat | Bottom sheet (slides up from bottom, can be minimized to a pill) |
| Photo gallery | Full-screen swipe with pinch-to-zoom |
| Filter panel | Full-screen overlay, slide up from bottom |
| Property detail | Stacked single-column; photo gallery takes full width |
| Pull-to-refresh | On listing feed |
| Swipe gestures | Left/right on listing cards to save/dismiss (optional) |

---

## 7. Implementation sequence (UX slice dependencies)

```
                    UX-01 (admin spec) ✓
                       │
                    UX-02 (beta page) ✓ → waiting verify
                       │
                    UX-03 (live API) ✓ → waiting verify
                       │
               ┌───────┴────────┐
               │                │
            UX-06 (this spec)  UX-04 (Bulgaria LUN) ← blocked BD-06, DBG-05
               │                │
               │            UX-07 (3D map) ← blocked BD-08
               │                │
               │            UX-08 (shop view) ← blocked BD-12
               │                │
               │            UX-09 (property detail) ← blocked BD-11
               │                │
               │            UX-10 (user profiles) ← blocked BD-13
               │                │
               │            UX-11 (Vercel deploy) ← blocked BD-14
               │
               └── UX-05 (AI chat) ← blocked BD-07
```

---

## 8. Acceptance gate for this spec

- [x] All route pages described with wireframe
- [x] Component tree covers every planned page + marks built vs pending
- [x] Mobile responsive strategy defined per breakpoint
- [x] Design system tokens documented (preserving existing code)
- [x] Implementation sequence shows all UX slice dependencies
- [x] Each unbuilt component maps to a specific UX slice
