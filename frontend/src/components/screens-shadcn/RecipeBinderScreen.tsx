import React from "react";
import { useRecipeBinder } from "@/hooks";
import { type RecipeCard as RecipeCardType } from "@/data/mockData";
import { Button, Card, CardContent, Input } from "@/components/shadcn";
import { cn } from "@/lib/utils";

interface RecipeCardProps {
  readonly recipe: RecipeCardType;
  readonly onToggleFavorite: () => void;
}

const RecipeCardItem: React.FC<RecipeCardProps> = ({
  recipe,
  onToggleFavorite,
}) => {
  const difficultyColor = {
    Easy: "text-green-400",
    Medium: "text-yellow-400",
    Hard: "text-red-400",
  };

  return (
    <Card className="group relative overflow-hidden hover:shadow-xl transition-all cursor-pointer">
      {/* Image */}
      <div className="aspect-[4/3] overflow-hidden">
        <div
          className="w-full h-full bg-muted bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
          style={{ backgroundImage: `url('${recipe.image}')` }}
          role="img"
          aria-label={recipe.title}
        />
      </div>

      {/* Content */}
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg leading-tight group-hover:text-primary transition-colors">
            {recipe.title}
          </h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite();
            }}
            className="text-muted-foreground hover:text-red-500 transition-colors"
          >
            <span
              className="material-symbols-outlined"
              style={recipe.isFavorite ? { fontVariationSettings: "'FILL' 1" } : {}}
            >
              favorite
            </span>
          </button>
        </div>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-base">schedule</span>
            {recipe.time}
          </span>
          <span className={cn("flex items-center gap-1", difficultyColor[recipe.difficulty])}>
            <span className="material-symbols-outlined text-base">bar_chart</span>
            {recipe.difficulty}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

interface FilterPillProps {
  readonly label: string;
  readonly active: boolean;
  readonly onClick: () => void;
}

const FilterPill: React.FC<FilterPillProps> = ({ label, active, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-5 py-2 rounded-full font-semibold text-sm transition-colors whitespace-nowrap",
        active
          ? "bg-primary text-primary-foreground"
          : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
      )}
    >
      {label}
    </button>
  );
};

interface RecipeBinderScreenProps {
  readonly className?: string;
}

export const RecipeBinderScreen: React.FC<RecipeBinderScreenProps> = ({
  className = "",
}) => {
  const {
    filteredRecipes,
    activeFilter,
    setActiveFilter,
    searchQuery,
    setSearchQuery,
    toggleFavorite,
    filters,
  } = useRecipeBinder();

  return (
    <div
      className={cn(
        "relative flex min-h-screen flex-col overflow-x-hidden bg-background",
        className
      )}
    >
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-3xl">
                restaurant_menu
              </span>
              <h1 className="text-xl font-bold tracking-tight">Recipe Binder</h1>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon">
                <span className="material-symbols-outlined">account_circle</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Search */}
        <div className="mb-10 max-w-3xl mx-auto">
          <div className="relative group">
            <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors">
              auto_awesome
            </span>
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your binder with natural language (e.g., 'Quick spicy chicken dinner')..."
              className="pl-12 text-lg shadow-sm"
            />
          </div>
        </div>

        {/* Filters & Sort */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {filters.map((filter) => (
              <FilterPill
                key={filter}
                label={filter}
                active={activeFilter === filter}
                onClick={() => setActiveFilter(filter)}
              />
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Sort by:
            </span>
            <button className="flex items-center gap-1 text-sm font-medium hover:text-primary transition-colors">
              Recent <span className="material-symbols-outlined text-sm">expand_more</span>
            </button>
          </div>
        </div>

        {/* Recipe Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredRecipes.map((recipe) => (
            <RecipeCardItem
              key={recipe.id}
              recipe={recipe}
              onToggleFavorite={() => toggleFavorite(recipe.id)}
            />
          ))}
        </div>
      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <Button size="lg" className="rounded-full px-6 shadow-lg hover:shadow-primary/30 hover:scale-105 transition-all">
          <span className="material-symbols-outlined">add</span>
          Add Recipe
        </Button>
      </div>
    </div>
  );
};

export default RecipeBinderScreen;
