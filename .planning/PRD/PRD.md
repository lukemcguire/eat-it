# Eat It - MVP PRD

### TL;DR

Eat It delivers a privacy-respecting, self-hostable web app for storing,
searching, and organizing recipes, and for managing collaborative smart shopping
lists. Built for home cooks and families who value control over their data and
flexibility in food planning, it leverages proven recipe parsing solutions, uses
AI to supercharge recipe search, and enables seamless multi-user grocery
planning—without unnecessary complexity or bloat.

---

## Goals

### Business Goals

- Launch a reliable, open-source MVP of Eat It for self-hosting by individual
  users and families within 4 weeks.

- Achieve at least 50 self-hosted deployments within 3 months of release.

- Demonstrate extensibility and community engagement to enable future feature
  contributions.

- Keep ongoing support/maintenance burden minimal by leveraging stable
  third-party parsing and proven patterns.

- Prove demand and elicit feedback for enhancements (e.g., media upload, richer
  AI features).

### User Goals

- Effortlessly import recipes from web links using robust, existing recipe
  parsing tools in Eat It.

- Quickly search and retrieve saved recipes with AI-powered, natural language
  queries.

- Generate and edit shopping lists based on selected recipes, with combined
  ingredient counts and easy checklist management.

- Enable family members or roommates to collaboratively view and update shared
  shopping lists (real-time sync not required in MVP).

- Trust that all data is stored locally with no third-party analytics or unknown
  data sharing.

### Non-Goals

- No development of custom or in-house recipe parsing—Eat It will rely entirely
  on third-party/open source parsers.

- No image, video, or file upload/import in MVP (future phase).

- No native mobile apps in MVP; only a responsive mobile-friendly web interface.

- No real-time or live collaborative document editing (edge case for future).

---

## User Stories

**Persona 1: Home Cook (Primary)**

- As a home cook, I want to import recipes from my favorite websites, so that I
  can keep all my recipes in one place.

- As a home cook, I want to use natural language search (e.g., “vegetarian
  dinner for 4”), so that I can quickly find the right recipe for my needs.

- As a home cook, I want to add recipes to a shopping list, so that buying
  groceries for meal prep is fast and organized.

- As a home cook, I want to see my shopping list on my phone or tablet, so I can
  shop efficiently.

**Persona 2: Co-Shopper (Partner, Roommate, Family)**

- As a co-shopper, I want to see and check off groceries from a shared list, so
  we avoid buying duplicates.

- As a co-shopper, I want to add items to the list even if I don’t cook, so I
  can participate in planning.

**Persona 3: Organizer/Early Adopter**

- As an organizer, I want to self-host Eat It on my own device, so that all data
  stays under my control.

- As an organizer, I want to export or back up my recipes and shopping lists, so
  that I own my data.

---

## Functional Requirements

- **Recipe Import & Management (Priority: High)**
  - **Web Recipe Import:** Users paste a recipe URL; Eat It uses an existing
    parser (e.g., open source recipe-scraper libraries) to extract structured
    data.

  - **Manual Recipe Entry:** For sites that can’t be parsed, users can add or
    edit recipes manually via a form.

  - **Recipe Storage:** Recipes are saved locally in a structured format (JSON
    or similar).

  - **Notes and Ratings:** Users can add private notes and give ratings, but
    these are applied at the individual recipe level only and are not connected
    to shopping lists.

  - **Decision to Finalize:** Should newly parsed recipes be added to the recipe
    binder automatically (with the user able to remove unwanted ones), or should
    saving always require explicit user action to save the recipe? This workflow
    must be decided before MVP implementation.

- **AI-Powered Search (Priority: High)**
  - **Natural Language Search:** Local/integrated AI enables users to search
    recipes with queries like “gluten-free dessert” or “quick breakfast for
    two.”

  - **Keyword/Tag Search:** Support for simple keyword filtering as fallback.

- **Smart Shopping List (Priority: High)**
  - **Recipe → Shopping List:** Users can select one or more recipes and
    auto-generate a shopping list with ingredients deduplicated and quantities
    summed.

  - **Manual List Editing:** Users can add/remove/edit items, adjust quantities,
    mark items as purchased.

  - **Checklist View:** Mobile/tablet-optimized list with check-off support.

- **Collaboration (Priority: Medium)**
  - **User Accounts (Optional for MVP):** Simple login, or single-user mode with
    shareable shopping list link or PIN.

  - **Multi-Device Access:** Shopping list accessible from multiple
    browsers/devices within the same local network or from a cloud-hosted
    self-install.

  - **Basic List Sync:** Instant or near-instant updates to the shopping list
    when multiple users are accessing at once (refresh to sync; no real-time
    websockets in MVP).

- **Exclusions / Not in MVP:**
  - Image/video parsing, uploading, or rich media display.

  - Real-time collaborative document editing.

  - Native mobile app.

  - Integrated third-party shopping or delivery services.

---

## User Experience

**Entry Point & First-Time User Experience**

- Users self-host Eat It by following simple setup instructions (docker-compose,
  single binary, or cloud deploy).

- On initial launch, a minimal onboarding screen explains recipe import and list
  management features; optionally, a sample recipe is provided.

- No forced sign-up—optional local login or guest mode.

**Core Experience**

- **Step 1:** User adds a new recipe.
  - UI has a clear “Add Recipe” button with options to “Paste URL” or “Enter
    Manually.”

  - User pastes a recipe link and clicks “Import.” The system attempts to parse
    using selected parser(s); errors are handled gracefully (with user feedback
    and option to edit/fix fields manually).

  - After import, user confirms details (title, ingredients, steps) and saves
    the recipe to their collection.

- **Step 2:** User searches for recipes.
  - Search bar supports typed natural language queries or keyword filters.

  - AI matches queries to saved recipes; results are sorted by relevance.

  - Results show short preview cards for each recipe.

- **Step 3:** User selects recipes to plan meals.
  - Checkboxes or “Add to List” actions let user select multiple recipes to
    include in upcoming shopping.

- **Step 4:** User generates a smart shopping list.
  - Ingredient lines from selected recipes are merged (e.g., all “eggs” get
    summed; quantities and units are normalized if possible).

  - User can add extra items, edit entries, or delete items directly on the
    list.

- **Step 5:** User (and co-shoppers) access the shopping list from any device.
  - List view is optimized for mobile, stresses touch targets and high contrast.

  - Tap to check items off; changes are saved immediately.

- **Step 6:** (Optional) Export/Bulk backup/restore recipes and shopping lists.

**Advanced Features & Edge Cases**

- If recipe parsing fails, users receive meaningful error messages and can
  complete import by hand.

- Duplicate recipe detection/warning.

- User-initiated backup/export of data as JSON or CSV.

- Handling browser storage limits or device sync errors.

**UI/UX Highlights**

- Highly responsive web interface; mobile-first checklist experience.

- Color contrast and large tap targets for easy, safe use during shopping.

- Clear “Import Recipe” and “Add to Shopping List” CTAs.

- No hidden actions—minimal clicks required to accomplish core tasks.

- All features accessible from both desktop and mobile browsers.

- Privacy notice: No telemetry or analytics by default; user controls all data.

---

## Narrative

Maria is the family chef and the tech-savvy one in her household. She’s grown
frustrated with “free” recipe sites that bombard her with pop-ups and ads, and
worries about the privacy of her saved meal plans. Wanting total control and a
clutter-free experience, she sets up Eat It on her home server—simple and fast.

With Eat It up and running, Maria imports recipes straight from her favorite
food blogs in seconds—no more copy-pasting text or dealing with unstructured
screenshots. When it’s time to plan the week’s meals, she searches “vegetarian
weeknight dinner” and instantly finds her best matches. With a few clicks, she
selects all needed recipes and generates a single, neatly organized shopping
list.

On her next grocery trip, Maria shares a link with her partner, letting them
split the shopping. Both check items off on their own phones, confident they
won’t miss or double up on anything. The whole kitchen routine feels smoother,
and best of all, Maria knows her recipe data never leaves her house. She feels
empowered, organized, and in control—exactly the outcome both she and the
product creator envisioned.

---

## Success Metrics

**User-Centric Metrics**

- Number of recipes imported per user per week (track usage and stickiness)

- Percentage of users accessing via mobile devices (validate mobile-first
  design)

- Weekly active users across devices (households making use of
  sharing/collaboration)

- Net Promoter Score (NPS) or direct feedback on usability and data privacy

**Business Metrics**

- Self-hosted deployments of Eat It (measured via opt-in ping, community
  reports, or download stats)

- Community star ratings/watchers/contributors (e.g., GitHub activity)

- User-submitted feature requests and participation in feedback surveys

**Technical Metrics**

- App uptime/reliability (target: >99% for self-hosted environments under normal
  use)

- Recipe parse/import success rate (target: >90% for supported recipe sites)

- Bug rate—number/severity of user-reported critical errors in MVP (<5/month)

**Tracking Plan**

- Recipe import events (success/failure, site sources)

- Search events and query types

- Shopping list creation and item check-off events

- Export/backup events

- (No user data is tracked or shared externally unless user opts in for usage
  data)

---

## Technical Considerations

### Technical Needs

- Use open-source recipe parsing tools or libraries (e.g., recipe-scrapers,
  existing Python/Node.js parsers)

- Local storage or embedded lightweight DB (e.g., SQLite, flat files) for
  recipes and lists

- Simple front-end (React, Vue, or Svelte) with responsive design

- Back-end API serving recipe import, storage, AI search, and shopping list
  endpoints

- Optional integration of lightweight AI/NLP components for local search (or
  local LLM if feasible)

### Integration Points

- Connect to open-source recipe parsers (not building own)

- Enable optional export/import via standard data formats (JSON, CSV)

- Future planning: Modular API layer to allow extension (e.g., image OCR for
  later phase)

### Data Storage & Privacy

- All user data stored locally within user’s device/server by default

- No third-party analytics or cloud data transmission

- Users maintain full read/write/export access to their data

- Compliance with principle of user data sovereignty (no legal compliance
  needed, but designed for privacy by default)

### Scalability & Performance

- MVP designed for up to 5–10 concurrent users per self-host; household use
  cases

- Minimal hardware requirements to ensure easy hosting (e.g., Raspberry Pi)

- Fast, <1s search/response time for up to several thousand saved recipes

### Potential Challenges

- Handling parsing errors (graceful fallback, user editing)

- Mobile browser quirks (testing required)

- Educating users on self-hosting if they’re not tech-savvy

- Avoiding accidental data loss (backup/restore approach)

---

## Milestones & Sequencing

### Project Estimate

- Medium: 2–4 weeks (solo builder or very small team)

### Team Size & Composition

- Extra-small: 1 person who does everything (core build, design, light docs,
  testing)

- For extended/future features: add 1 developer (2-person team at most for v1.x)

### Suggested Phases

**Phase 1: MVP Build & Internal Testing (2 weeks)**

- Key Deliverables: Core recipe import, storage, search, and shopping list
  functions; mobile-friendly UI.
  - Owner: Solo builder

- Dependencies: Select and integrate open-source recipe parser; pick
  front-end/back-end stack.

**Phase 2: Community Release & Feedback (1 week)**

- Key Deliverables: Basic setup/install guide, sample deploy configs, enable
  feedback channel (e.g., issues on GitHub)

- Dependencies: Initial testing, lightweight documentation.

**Phase 3: Rapid Improvement & Extensibility Planning (1 week)**

- Key Deliverables: Address critical bug reports, refine UX based on feedback,
  publish API docs for future add-ons/extensions.

- Dependencies: User feedback, prioritization.

**Future Phases (Post-MVP, expand as needed)**

- Media upload: Allow recipe images/photos

- Native mobile apps (iOS/Android wrappers or PWA enhancements)

- Advanced collaboration: Real-time multi-user editing, notifications

- Integration with grocery delivery/pickup platforms

- OCR/import from screenshots or PDFs

---
