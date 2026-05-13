# Social Media Source Discovery And Reliable Access Paths

Date: 2026-05-13
Owner: `scraper_sm`
Scope: Bulgaria real-estate lead-intelligence overlays across Facebook, Viber, Telegram, WhatsApp, and Instagram.

This is a public-discoverable seed inventory. It is not a claim that every private, closed, login-gated, invite-only, or non-indexed group has been found. Those cannot be enumerated or scraped safely.

## Executive Decision

FACT — The project can safely prepare social lead intelligence, but not broad private/social scraping.

INTERPRETATION — The reliable path is platform-native authorization, explicit consent, partner/manual capture, and redacted review queues. HTML scraping, login/session automation, private group scraping, and unofficial messenger automation are blocked.

HYPOTHESIS — Telegram public channels have the best near-term automation value; Facebook groups have high lead value but must be manual/consent only; Instagram is useful mostly for agency/project branding; Viber/WhatsApp should be business opt-in or direct partner paths.

GAP — API credentials, app review approvals, bot/channel admin permissions, consent artifacts, and production review tables are not verified.

## Platform Access Rules

| Platform | Reliable route | Blocked route | Storage class |
|---|---|---|---|
| Telegram | Bot API where bot is permitted, or separately approved Telegram API/TDLib public-channel client | private channels, DMs, hidden member/group scraping | `lead_thread`, `lead_message`, `source_link_candidate` |
| Facebook Pages | Meta Graph API with approved Page access, or manual review | HTML scraping without Meta permission | manual/API review candidate |
| Facebook Groups | manual/consent only | autonomous group scraping, login-gated scraping, old Groups API assumptions | manual review candidate |
| Instagram | Instagram Graph API Business Discovery for professional accounts, or manual review | profile HTML scraping / unofficial APIs | brand/project signal overlay |
| Viber | commercial Viber bot or Business Messages with opted-in users | arbitrary community scraping | opt-in lead evidence |
| WhatsApp | WhatsApp Business Platform webhooks for opt-in business conversations | personal group/channel/DM scraping | opt-in lead evidence |

## Candidate Inventory

Machine-readable file: `data/social_media_intelligence_candidates.json`.

### Telegram

| Candidate | URL | Signal | Route | Priority |
|---|---|---|---|---|
| rentvarna | https://t.me/rentvarna | Varna rent leads | official API candidate | high |
| Аренда квартир Варна | https://t.me/varnarents | Varna rent leads | official API candidate | high |
| Квартири под наем - Варна | https://t.me/kvartirivarna | Varna rent leads | API/manual, verify type | high |
| Аренда Rents Miete Варна | https://t.me/addressbg | agency reposts with source links | official API candidate | high |
| BulgaRoom | https://t.me/bulgaroom | BG listing leads | official API candidate | medium |
| Imotni.com | https://t.me/imotnicom | market/news/education | official API candidate | medium |
| Недвижимость в Болгарии | https://t.me/nedvizhimostbolgaria | Black Sea sale leads | official API candidate | medium |
| Варна - Аренда чат | https://t.me/varna_rent_chat | Varna rent chat | manual/admin permission only | medium |
| Аренда Варна / Rent Varna | https://t.me/realestateagencyvarna | rent leads | official API candidate | medium |
| Real Estate Varna | https://t.me/varna_nedvizhimost | rent/sale leads | official API candidate | medium |
| real_estate_varna777 | https://t.me/real_estate_varna777 | rent/sale leads | official API candidate | medium |
| real_estate_bg | https://t.me/real_estate_bg | BG property leads | verify first | medium |
| ads_in_bulgaria | https://t.me/ads_in_bulgaria | mixed classifieds | relevance gate first | low |
| bgvarna_en | https://t.me/bgvarna_en | expat/community signal | relevance gate first | low |

### Facebook

| Candidate | URL | Signal | Route | Priority |
|---|---|---|---|---|
| Квартири под наем без брокер - Варна | https://www.facebook.com/groups/826804772394767/ | Varna rent leads | manual/consent only | high |
| Квартири и Имоти Под Наем - ВАРНА | https://www.facebook.com/groups/1396172977208190/ | Varna rent leads | manual/consent only | high |
| Квартири и съквартиранти в София БЕЗ БРОКЕР | https://www.facebook.com/groups/1768589073411714/ | Sofia rent/roommate leads | manual/consent only | medium |
| Апартаменти под наем в София | https://www.facebook.com/groups/956611284504149/ | Sofia rent leads | manual/consent only | medium |
| Квартири под наем БЕЗ Посредник - Пловдив | https://www.facebook.com/groups/KvartiriPlovdiv/ | Plovdiv rent leads | manual/consent only | medium |
| Bulgarian cheap properties | https://www.facebook.com/groups/331887975451394/ | Bulgaria sale/rent | manual/consent only | medium |
| Вили под наем в България / BookVilla.bg | https://www.facebook.com/groups/3037259826530075/ | villa/STR leads | partner/manual | low |
| RealEstateVarna1 | https://www.facebook.com/RealEstateVarna1 | Varna agency posts | Graph API if approved/manual | medium |
| Property.bg by Suprimmo | https://www.facebook.com/www.property.bg/ | agency/project posts | Graph API if approved/manual | medium |
| Address official Facebook | Address.bg homepage social link | agency posts | resolve exact page + Graph/manual | medium |

### Instagram

| Candidate | URL | Signal | Route | Priority |
|---|---|---|---|---|
| bulgarianproperties.bg | https://www.instagram.com/bulgarianproperties.bg/ | agency/project branding | Business Discovery/manual | medium |
| bulgarianpropertiesagency | https://www.instagram.com/bulgarianpropertiesagency/ | agency branding | Business Discovery/manual | low |
| suprimmo.bg | https://www.instagram.com/suprimmo.bg/ | agency/project branding | Business Discovery/manual | medium |
| suprimmo.varna | https://www.instagram.com/suprimmo.varna/ | Varna agency branding | Business Discovery/manual | medium |
| suprimmo.burgas | https://www.instagram.com/suprimmo.burgas/ | Burgas agency branding | Business Discovery/manual | medium |
| luximmo.bg | https://www.instagram.com/luximmo.bg/ | luxury/project branding | Business Discovery/manual | medium |
| luximmo.burgas | https://www.instagram.com/luximmo.burgas/ | luxury/project branding | Business Discovery/manual | low |
| rentica.bg | https://www.instagram.com/rentica.bg/ | rental branding | Business Discovery/manual | low |
| real_estate_varna_ | https://www.instagram.com/real_estate_varna_/ | Varna rent/sale brand signal | verify professional status/manual | medium |
| Address official Instagram | Address.bg homepage social link | agency branding | resolve exact profile + Graph/manual | medium |

### Viber

Viber candidates are invite/community seeds only. They are not consent to scrape.

| Candidate | URL/source | Signal | Route | Priority |
|---|---|---|---|---|
| Registry Viber seed 1 | source registry invite URL | rent/sale leads | commercial bot/manual consent only | low |
| Registry Viber seed 2 | source registry invite URL | rent/sale leads | commercial bot/manual consent only | low |
| Registry Viber seed 3 | source registry invite URL | rent/sale leads | commercial bot/manual consent only | low |
| Registry Viber seed 4 | source registry invite URL | rent/sale leads | commercial bot/manual consent only | low |
| Primea/Imoti Premier Viber offer channel | public alo.bg snippets | agency early-offer leads | partner/manual consent only | medium |

### WhatsApp

| Candidate | URL/source | Signal | Route | Priority |
|---|---|---|---|---|
| Registry WhatsApp opt-in group seed | source registry invite URL | sale/rent leads | WhatsApp Business Platform or manual consent only | low |

No reliable public WhatsApp group discovery path was found in this run. Treat WhatsApp as business opt-in intake, not a group-scraping source.

## Reliable Acquisition Design

1. Telegram first: validate each public candidate with a no-storage probe, then add fixtures from permitted public channel messages. Live worker remains blocked until API route, bot/session, redaction, rate limit, and debugger approval exist.
2. Facebook groups: keep as manual research targets only. Operators can paste/export a redacted sample into fixtures with consent/source notes. No browser/session crawler.
3. Facebook pages: use Graph API only after approved page/public-content permissions, otherwise manual review.
4. Instagram: use Business Discovery for professional accounts where allowed. Use profile posts only as brand/project signals unless a post links to a canonical source URL.
5. Viber: create an opt-in business/bot intake path; do not join and scrape communities.
6. WhatsApp: create WhatsApp Business webhook intake for owners/agents who opt in; do not read groups or DMs via unofficial automation.

## Data Analyst Handoff Metrics

- `candidate_total_by_platform`
- `validated_public_candidate_count`
- `official_api_ready_count`
- `manual_consent_only_count`
- `blocked_private_or_group_count`
- `redaction_failure_count`
- `lead_only_count`
- `candidate_single_unit_count`
- `suspected_multi_unit_count`
- `source_link_candidate_count`
- `promotion_blocked_count`

## Sources Reviewed

- Telegram Bot API docs: https://core.telegram.org/bots/api#getting-updates
- Instagram Business Discovery docs: https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/business-discovery
- Viber REST Bot API docs: https://developers.viber.com/docs/api/rest-bot-api/
- WhatsApp Cloud API SDK receiving-message docs: https://whatsapp.github.io/WhatsApp-Nodejs-SDK/receivingMessages/
- Meta Automated Data Collection Terms: https://www.facebook.com/legal/automated_data_collection_terms
- Facebook Groups API deprecation summary with Meta announcement link: https://www.sprinklr.com/help/articles/getting-started-facebook/meta-deprecates-facebook-groups-api/66229eb25f9dd9599d632712
- Address.bg social links and agency context: https://address.bg/
- Public Telegram web previews and public search results for listed Telegram candidates.
- Public web search results for Facebook group/page candidates and Viber invite snippets.

## Next Tasks

- `SM-14`: Telegram public candidate validation and fixture expansion.
- `SM-15`: Meta Facebook/Instagram manual/API route pilot.
- `SM-16`: WhatsApp/Viber opt-in business intake design.

## Hard Blocks

- No private groups, DMs, login-gated sessions, mass accounts, KYC/CAPTCHA bypass, or unofficial messenger automation.
- No canonical listings from social media without review and accepted single-unit evidence.
- No public dashboard counts mixing S&M leads with Action1 marketplace inventory.
