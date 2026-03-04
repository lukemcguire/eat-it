# Eat It - UI Components

React components generated from Stitch designs for the Eat It recipe management application.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (custom React components)
npm run dev

# Start development server (shadcn/ui components)
npm run dev:shadcn
```

## Project Structure

```
src/
├── components/
│   ├── ui/                    # Custom shared UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── ...
│   ├── shadcn/               # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── tabs.tsx
│   │   └── ...
│   ├── shopping/             # ShoppingListScreen (custom)
│   ├── recipe-detail/        # RecipeDetailScreen (custom)
│   ├── recipe-binder/        # RecipeBinderScreen (custom)
│   ├── recipe-import/        # RecipeImportScreen (custom)
│   └── screens-shadcn/       # Screen components using shadcn/ui
├── hooks/
│   ├── useShoppingList.ts
│   ├── useRecipeBinder.ts
│   └── useRecipeImport.ts
├── data/
│   └── mockData.ts           # Static content extracted from designs
└── lib/
    └── utils.ts              # cn() utility for shadcn/ui
```

## Two Implementations

### 1. Custom React Components (`src/components/*/`)

Lightweight, custom components built from scratch with Tailwind CSS:
- Direct Tailwind class usage
- No external dependencies beyond React
- Minimal bundle size

**Entry point:** `src/App.tsx` + `src/index.tsx`

### 2. shadcn/ui Components (`src/components/shadcn/` + `src/components/screens-shadcn/`)

Components built using shadcn/ui patterns:
- Radix UI primitives for accessibility
- CSS variables for theming
- `class-variance-authority` for variant management
- Dark mode support via `.dark` class

**Entry point:** `src/AppShadcn.tsx` + `src/index.shadcn.tsx`

## Components

### Screen Components

| Component | Description |
|-----------|-------------|
| `ShoppingListScreen` | Mobile-optimized shopping list with sections |
| `RecipeDetailScreen` | Full recipe view with ingredients and instructions |
| `RecipeBinderScreen` | Recipe collection grid with search and filters |
| `RecipeImportScreen` | URL-based recipe import with preview |

### shadcn/ui Components Used

| Component | Usage |
|-----------|-------|
| `Button` | Primary/secondary actions, FABs |
| `Card` | Recipe cards, content containers |
| `Input` | Search, URL import |
| `Checkbox` | Shopping list items |
| `Badge` | Tags, labels |
| `Tabs` | Navigation tabs |
| `Avatar` | User profile |
| `Table` | Ingredient lists |
| `Separator` | Visual dividers |

## Design Tokens

See `style-guide.json` for the complete design system including:
- Color palette (primary, backgrounds, surfaces, borders)
- Typography (Space Grotesk, Manrope)
- Border radius scale
- Spacing tokens

### shadcn/ui Theme Variables

Defined in `src/index.shadcn.css`:
- `--background`, `--foreground`
- `--primary`, `--primary-foreground`
- `--secondary`, `--secondary-foreground`
- `--muted`, `--muted-foreground`
- `--border`, `--input`, `--ring`

## Architecture Notes

- **Dark mode first**: All components use dark mode classes by default
- **Mobile-responsive**: Shopping list uses a 480px max-width mobile container
- **Modular hooks**: Business logic isolated in custom hooks
- **Type-safe**: All props use `Readonly<T>` interfaces

## Switching Between Implementations

The project supports both implementations simultaneously:

```bash
# Custom React components
npm run dev          # Uses src/index.tsx → src/App.tsx

# shadcn/ui components
npm run dev:shadcn   # Uses src/index.shadcn.tsx → src/AppShadcn.tsx
```

## Installation Commands

To add more shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

This will:
1. Download component source to `src/components/shadcn/`
2. Install required Radix UI dependencies
3. Update the component exports
