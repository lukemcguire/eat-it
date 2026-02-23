# Future Features co-planning

### Consultant:

Here’s my recommended order for stretch/future features—ranked by a combination
of user impact, feasibility, and likely technical complexity. I’ll frame my
reasoning as I go.

1. Image/OCR-Based Recipe Import This is both a technical challenge and a major
   differentiator. People want to snap photos of grandma’s cookbook,
   screenshots, or magazine recipes.

- Impact: High—solves a real offline and “legacy recipe” need.
- Complexity: Moderate-high—open-source OCR tools exist (Tesseract, etc.), but
  combining OCR, semantic understanding, and error handling is nontrivial.
- Why not first?. Technical risk is higher than building text/URL-based import,
  so do this once core parsing/UI are stable.

2. Real-Time Collaborative Editing Enables true multi-device, multi-person
   editing (like live check-off or co-planning a list).

- Impact: Medium-high, especially for families/couples.
- Complexity: Moderate—needs websocket or polling, good transaction handling, UI
  for merge conflicts.
- Why not MVP? Adds infra and state-synchronization headaches best avoided
  early, but a meaningful “v2.”

3. Native Mobile Apps or PWA Enhancements Native apps grant push notifications,
   offline access, and better device integration. A strong PWA (Progressive Web
   App) gives many of the same wins (installable, works offline, can send basic
   notifications).

- Impact: Medium-high, especially for sustained engagement/shopping.
- Complexity: Moderate, depending on approach (PWA is easiest, full native is
  hardest).
- Recommendation: PWA wrap is “quick win;” only pursue full-native if you build
  serious traction.

4. Grocery Store Integration / Delivery Platform Sync Auto-send lists to
   Instacart or another platform for fulfillment.

- Impact: High for some, irrelevant to others (esp. the self-hosted crowd).
- Complexity: Medium-high, depends on APIs, region, and partnerships.
- Only pursue if users demand it and privacy posture can be maintained.

5. Plugin/Extension API for Power Users Enable user-contributed modules (diet
   filters, meal planners, export formats).

- Impact: Huge for an open-source project. Drives network/community effects.
- Complexity: High if you didn’t design for modularity at the start, more
  manageable otherwise.

6. Advanced AI/NLP for Recipe Categorization & Personal Recommendations
   Automatically tags cuisine, difficulty, “suggests next week’s menu.”

- Impact: High delight factor, but not as mission-critical as the import/collab
  flows.
- Complexity: High. Defer unless you or your community have AI/ML
  interest/capability.

**Opinion:**

Image/OCR import and real-time list shopping are top of the “should do next”
pile—they’re both directly tied to core user stories, and open you up for new
differentiation.

Would you like to add or reorder any items? How hungry are you for deep AI
features, or do you see this primarily as a “get the core right, then expand”
project?

### Developer

I like all of those, I might reorder them slightly (1 - 2 - 6 - 5 - 3 - 4) and I
would also maybe slot in automatic parsing from video recipes
(instagram/tiktok/youtube) after real-time collaboration. But I do want to make
sure that it is built to be extensible from the start.

### Consultant

That’s a well-reasoned reshuffle. Prioritizing AI/NLP after the core
import/collab flows is smart—it future-proofs “Eat It” to support advanced
search/categorization as AI/ML tools mature, while real-time collaboration and
media parsing directly enhance daily usability and acquisition.

Your revised stretch roadmap:

1. Image/OCR-Based Recipe Import
1. Real-Time Collaborative Editing
1. jAdvanced AI/NLP for Recipe Categorization & Recommendations
1. Plugin/Extension API for Power Users
1. Native Mobile Apps / PWA Enhancements
1. Grocery Store/Delivery Platform Integration
1. Automatic Parsing from Video Recipes (Instagram, TikTok, YouTube—after
   real-time collab, likely paired closely with image/OCR extension)

And you’re absolutely right: extensibility is non-negotiable for a self-hosted,
open-source product. That means:

- Modular API/data layer from day one (not tightly coupling the front-end to any
  one source/parser).
- Clear, documented interfaces for plugins/add-ons (even if only you are
  authoring them at first).
- Recipe and shopping list schemas designed for future metadata (images, tags,
  time, difficulty, etc.).
- Avoiding shortcut “hacks” (e.g., stuffing note fields with structured data)
  that would make future contributions brittle.

In practice, this might mean spending an extra day or two early on designing
your core models—the kind of investment that will seriously pay off. You can
always delay exposing a public “plugin” API, but bake in the boundaries from
MVP.

Do you want sample technical scoping/architecture suggestions for extensibility,
or would you rather move to launch with this prioritized stretch list—and
revisit modularity in technical design reviews?

### Developer

I'd like sample technical scooping/architecture suggestions for extensibility. I
want to make sure that's considered from the start.

### Consultant

Excellent. Extensibility is easiest to achieve if you build it into your
architecture and data models early—even if you ship only one plugin (or none) in
the MVP. Here’s a structured set of recommendations and practical “spikes”:

**1. Modularity in Architecture** **API-Layer Modularity:** Design a clear
boundary between your core API and add-on functions.

- Your API should route feature calls (e.g., importers, search, list-gen) to
  handler “modules” packed as classes or functions.
- Future contributors should be able to add or override a handler without
  rewriting the core.

**Example:**

- Use a “provider” pattern for recipe importers: each provider (web parser, OCR
  importer, etc.) implements a specific importer interface.
- The API layer “dispatches” to all available providers and returns the best
  result.

**2. Plugin/Extension Points** **Explicit Plugin Directory:**

- At startup, Eat It scans a defined “plugins” folder (in filesystem or as
  importable Python/Node modules).
- Each plugin registers its type (importer, exporter, UI enhancement).
- Plugins get passed core app objects (the data store, API context) but are
  sandboxed: they can’t crash the core app.

**Event Hook System:**

- Define standard events (“recipe_saved”, “shopping_list_finalized”, etc.).
- Plugins can subscribe to these and execute code when events happen (similar to
  middleware or webhooks).

**3. Schema & Data Layer Extensibility** **Flexible Data Schemas:**

- Use a document or semi-structured DB model (like JSON fields in SQLite, or
  Mongo-style docs) for recipes and lists.
- Always allow “metadata” or “extras” fields for arbitrary plugin data, tags,
  images, source info.
- Never store plugin data in ad-hoc ways (“hacky” fields or overloaded text
  boxes).

**Versioned Data Models:**

- Build in a model version (e.g., “recipe.schema_version: 1”) to support
  migration if/when schema changes.

**4. Decoupled Front-End Extension** **Front-end Plugin Loader:**

- Offer a way for UI/plugin code (JS/CSS) to be loaded dynamically (e.g., a
  plugins manifest that gets parsed at boot by the SPA or injected at run-time).
- Expose simple front-end hooks: custom components, new list views, etc.

**API-Driven Extensions:**

- If your plugins are mostly API-side, ensure the front-end can handle unknown
  new fields gracefully (e.g., shows “extras” or plugin-generated fields in an
  expandable section).

**5. Distribution and Doc Conventions**

- Ship a “plugin template” in your repo: docs, a minimal example, and a test
  plugin.
- Tag entry points/types (importer, exporter, enhancer, etc.) in plugin
  metadata.
- Document which core events, schemas, and API endpoints are safe to extend or
  override.

**Practical Next Steps:**

- For MVP, implement at least one “external provider” (e.g., use both your
  default parser and an optional community/specialized scraper).
- Create one dummy plugin as a test (e.g., auto-tag imported recipes by
  keyword).
- Expose a config file or admin UI that enumerates loaded plugins and allows
  enabling/disabling at runtime.

**Opinion:**

Investing even 1–2 days in a minimal version of this (API handler registry,
plugin directory, metadata in schemas) makes future additions and community work
10x easier and will make your product genuinely resilient to shifting needs.
