# Design System: Eat It
**Project ID:** 4793790745632304119

This design system synthesizes patterns from four key screens: Shopping List
(Synchronized Blue), Recipe Detail (Synchronized Blue), Recipe Binder
(Finalized Nordic), and Recipe Import (Finalized Nordic). The system blends two
complementary themes optimized for dark-mode recipe management.

---

## 1. Visual Theme & Atmosphere

**Overall Mood:** Nordic Minimalist with Technical Precision

The interface evokes a clean, Scandinavian-inspired aesthetic with deep,
blue-leaning dark backgrounds that feel cozy yet modern. The design balances
density with breathing room—information is well-organized without feeling
sparse. The atmosphere is calm and focused, ideal for meal planning tasks.

**Key Atmosphere Descriptors:**

- **Deep & Immersive:** Rich navy-charcoal backgrounds create depth
- **Clean & Organized:** Clear visual hierarchy with generous whitespace
- **Subtle Elegance:** Muted accent colors with strategic bright blue highlights
- **Touch-Friendly:** Generous tap targets and pill-shaped interactive elements

---

## 2. Color Palette & Roles

### Primary Actions & Accents

| Name | Hex | Role |
|------|-----|------|
| Synchronized Blue | `#207fdf` | Primary actions, active states, links (Space Grotesk screens) |
| Nordic Blue | `#3b82f6` | Primary actions, buttons, FABs (Manrope screens) |
| Ice Blue | `#a5c1d9` | Secondary text, muted labels, ingredient quantities |

### Backgrounds

| Name | Hex | Role |
|------|-----|------|
| Midnight Navy | `#0f1923` | Main dark background (Synchronized theme) |
| Charcoal Navy | `#0f172a` | Main dark background (Nordic theme) |
| Deep Charcoal | `#0b1219` | Alternative dark background for import screens |
| Surface Navy | `#1a2632` | Card backgrounds, elevated surfaces |
| Light Mist | `#f5f7f8` | Light mode background (if needed) |
| Soft Slate | `#f8fafc` | Light mode alternative background |

### Borders & Dividers

| Name | Hex | Role |
|------|-----|------|
| Muted Blue-Gray | `#2e4e6b` | Borders, dividers (Synchronized theme) |
| Slate Border | `#2d3d4d` | Alternative border color |
| Charcoal Border | `#334155` | Subtle dividers in Nordic theme |
| Dark Border | `#1e293b` | Deeper border for emphasis |

### Text Colors

| Name | Hex | Role |
|------|-----|------|
| White | `#ffffff` | Primary headings, important text |
| Off-White | `#f1f5f9` | Body text on dark backgrounds |
| Muted Slate | `#94a3b8` | Secondary text, captions, placeholders |
| Soft Gray | `#64748b` | Tertiary text, disabled states |

### Semantic States

| Name | Hex | Role |
|------|-----|------|
| Success Green | `#06f906` | Checkboxes, completion indicators (project accent) |
| Favorite Red | `#ef4444` | Heart/favorite icons on hover |

---

## 3. Typography Rules

### Font Families

**Space Grotesk** (Synchronized Blue theme)
- Used for: Shopping List, Recipe Detail
- Character: Technical, geometric, slightly condensed
- Weights: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

**Manrope** (Finalized Nordic theme)
- Used for: Recipe Binder, Recipe Import
- Character: Friendly, rounded, highly readable
- Weights: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (extrabold)

### Type Scale

| Element | Size | Weight | Tracking |
|---------|------|--------|----------|
| Page Title | `2.25rem` - `3rem` | 700-800 | Tight (`-0.025em`) |
| Section Heading | `1.5rem` | 700 | Tight |
| Card Title | `1.125rem` | 700 | Normal |
| Body Text | `1rem` | 400-500 | Normal |
| Caption/Label | `0.75rem` | 600-700 | Wide (`0.1em`) |
| Tab Label | `0.875rem` | 700 | Normal |

### Typography Patterns

- **Headings:** Bold weight with tight tracking for punchy, compact titles
- **Section Labels:** Uppercase, small size, wide tracking, muted color
- **Body:** Regular weight, comfortable line height (1.5-1.6)
- **Numbers in Steps:** Large, bold, circular badge treatment

---

## 4. Component Stylings

### Buttons

**Primary Button**
- Shape: Pill-shaped to gently rounded (`rounded-xl` = 0.75-1rem radius)
- Background: Synchronized Blue (`#207fdf`) or Nordic Blue (`#3b82f6`)
- Text: White, bold weight
- Padding: `py-4 px-6` (generous vertical padding)
- Shadow: Colored shadow at 20-30% opacity (`shadow-lg shadow-primary/30`)
- Hover: Slight scale up (`hover:scale-[1.02]`)
- Active: Scale down slightly (`active:scale-[0.98]`)

**Secondary/Icon Button**
- Shape: Rounded (`rounded-lg` = 0.5rem)
- Background: Surface Navy or transparent with border
- Size: `h-10 w-10` for icon buttons
- Hover: Background lighten/darken

**Floating Action Button (FAB)**
- Shape: Fully pill-shaped (`rounded-full`)
- Position: Fixed, bottom-right (`bottom-8 right-8`)
- Shadow: Prominent with color tint

### Cards/Containers

**Recipe Card**
- Shape: Gently rounded corners (`rounded-xl`)
- Background: Surface Navy or white in light mode
- Border: 1px solid border color
- Hover: Lift effect with enhanced shadow (`hover:shadow-xl`)
- Image: 4:3 aspect ratio, zoom on hover

**Content Card**
- Shape: More rounded (`rounded-2xl` = 1.5rem)
- Background: Semi-transparent dark surface
- Padding: `p-8` (generous internal spacing)
- Border: Subtle 1px border

**Section Header**
- Background: Slightly lighter/different tone than surface
- Padding: `px-6 py-2` (compact vertical, generous horizontal)
- Border: None, but creates visual separation

### Inputs/Forms

**Text Input**
- Shape: Rounded (`rounded-xl`)
- Background: Slightly lighter than surface or transparent
- Border: 1px subtle border
- Focus: 2px ring in primary color (`focus:ring-2 focus:ring-primary/50`)
- Padding: `py-4 pl-12 pr-4` (space for icon)

**Checkbox**
- Size: `h-6 w-6` (generous for touch)
- Shape: Slightly rounded corners
- Border: 1px in border color
- Checked: Primary color fill

### Navigation

**Tab Bar**
- Style: Underline indicator
- Active: Primary color underline (`border-b-2 border-primary`)
- Inactive: Transparent underline, muted text
- Mobile Nav: Bottom-fixed with icons + tiny labels

**Header**
- Height: `h-16` (64px)
- Background: Blurred, semi-transparent (`backdrop-blur-md`)
- Border: Bottom border only
- Sticky: Fixed to top

---

## 5. Layout Principles

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| Tight | `0.25rem` (4px) | Icon gaps, inline spacing |
| Compact | `0.5rem` (8px) | Small gaps, list spacing |
| Default | `1rem` (16px) | Standard gaps |
| Comfortable | `1.5rem` (24px) | Section gaps |
| Generous | `2rem` (32px) | Major sections |
| Spacious | `3rem` (48px) | Page sections |

### Grid System

- **Content Max-Width:** `max-w-7xl` (80rem) for full layouts
- **Content Max-Width:** `max-w-4xl` (56rem) for focused content
- **Mobile Container:** `max-w-[480px]` with centered layout
- **Grid Columns:** 1 → 2 → 3 → 4 responsive breakpoints
- **Card Grid Gap:** `gap-6` (1.5rem)

### Whitespace Philosophy

- **Generous Horizontal Padding:** `px-6` to `px-20` based on viewport
- **Vertical Rhythm:** Consistent `gap-6` or `gap-8` between sections
- **Card Internal Padding:** `p-5` to `p-8` for breathing room
- **Compact Lists:** `py-4` per item with dividers

### Responsive Behavior

- **Mobile-First:** Optimized for 480px mobile container
- **Breakpoints:** `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`
- **Layout Shift:** Single column → multi-column grid
- **Navigation:** Bottom tabs on mobile, top header on desktop

---

## 6. Interaction Patterns

### Hover Effects

- **Cards:** Subtle scale + shadow enhancement
- **Buttons:** Scale transform (1.02 up, 0.98 down)
- **Icons:** Color shift to primary or accent
- **Links:** Underline or color change

### Transitions

- **Duration:** `duration-500` for images, `duration-200` for UI
- **Easing:** Default Tailwind easing
- **Transform:** Scale for tactile feedback

### Icons

- **System:** Material Symbols Outlined
- **Weight:** 400 (regular)
- **Size:** `text-xl` to `text-3xl` based on context
- **Variation Settings:** `FILL` 0, `wght` 400

---

## 7. Special Elements

### Step Numbers (Instructions)

- Shape: Perfect circle (`rounded-full`)
- Size: `w-10 h-10`
- Background: Primary color
- Text: White, bold
- Hover: Scale up (`group-hover:scale-110`)

### Tags/Pills

- Shape: Fully rounded (`rounded-full`)
- Padding: `px-3 py-1` to `px-5 py-2`
- Background: Primary or muted surface
- Text: Small, semibold

### Floating Elements

- **Gradient Fade:** `bg-gradient-to-t from-background-dark/60 to-transparent`
- **Glass Effect:** `backdrop-blur-md` with semi-transparent background
- **Shadows:** Colored shadows for depth (`shadow-primary/20`)

---

## Quick Reference for Stitch Prompts

When generating new screens, describe the design as:

> A dark-mode Nordic-inspired interface with deep navy-charcoal backgrounds
> (#0f1923 or #0f172a), using Synchronized Blue (#207fdf) or Nordic Blue
> (#3b82f6) for primary actions. Typography uses Space Grotesk or Manrope with
> bold headings and tight tracking. Components feature gently rounded corners
> (0.5-1rem radius), pill-shaped buttons with colored shadows, and cards with
> subtle borders and hover lift effects. The aesthetic is clean, organized, and
> touch-friendly with generous spacing.
