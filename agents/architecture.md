# Real Estate Intelligence Engine - Orchestration Architecture

## System Overview
The system is a multi-agent, self-regulating pipeline designed to extract, parse, and analyze real estate data from Bulgarian web sources and social platforms.

## Agent Roles

### 1. Tier 1 Scraper Agent (The Harvester)
*   **Task**: Execute Playwright/BeautifulSoup crawls.
*   **Targets**: `olx_bg`, `luximmo`, `property_bg`, `suprimmo`, `yavlena`, Telegram/X.
*   **Output**: Raw HTML/JSON and cleaned structured data in `/data/raw`.
*   **Mechanism**: Uses the project-specific venv.

### 2. Tier 1 Debugger Agent (The Healer)
*   **Task**: Monitor scraper logs for 403, 404, or Parsing Errors.
*   **Action**: Inspect `raw.html`, update CSS/XPath selectors in `agents/config`, and verify the fix.
*   **Reporting**: Log all adaptations in `logs/debugger`.

### 3. Gemma4 Vision Agent (The Analyst)
*   **Task**: Image feature extraction.
*   **Scope**: Analyze property photos for quality, lighting, and structural integrity.
*   **Integration**: Triggered post-scraping via the orchestration loop.

### 4. Planner Agent (The Manager)
*   **Task**: Orchestration, documentation, and project oversight.
*   **Output**: Updates to `CoreWiki` and the project `README.md`.
*   **Approval**: Manages the Telegram-based human-in-the-loop (HITL) approval system.

## Data Flow
`Web Source` ➔ `Scraper Agent` ➔ `Raw Storage` ➔ `Parser/Debugger` ➔ `Structured Data` ➔ `Gemma4 Vision` ➔ `Final Intelligence Report`
