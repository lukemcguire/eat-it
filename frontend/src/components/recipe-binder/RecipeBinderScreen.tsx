import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useRecipes } from '@/hooks/useRecipes';
import { RecipeDetailModal } from '@/components/RecipeDetailModal';
import { toast } from 'sonner';
import { Icon, Button, Input } from '../ui';
import type { Recipe } from '@/types/recipe';

interface RecipeCardProps {
  readonly recipe: Recipe;
  readonly onClick: () => void;
}

const RecipeCardItem: React.FC<RecipeCardProps> = ({ recipe, onClick }) => {
  // Format time from prep_time and/or cook_time
  const formatTime = () => {
    const times = [];
    if (recipe.prep_time) times.push(recipe.prep_time);
    if (recipe.cook_time) times.push(recipe.cook_time);
    return times.length > 0 ? times.join(' + ') : null;
  };

  const displayTime = formatTime();

  return (
    <div
      onClick={onClick}
      className="group relative flex flex-col bg-white dark:bg-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 hover:shadow-xl transition-all cursor-pointer"
    >
      {/* Image */}
      <div className="aspect-[4/3] overflow-hidden">
        {recipe.image_url ? (
          <div
            className="w-full h-full bg-slate-200 dark:bg-slate-800 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
            style={{ backgroundImage: `url('${recipe.image_url}')` }}
            role="img"
            aria-label={recipe.title}
          />
        ) : (
          <div className="w-full h-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
            <Icon name="restaurant_menu" className="text-slate-400 text-4xl" />
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg leading-tight group-hover:text-primary transition-colors text-slate-900 dark:text-slate-100">
            {recipe.title}
          </h3>
        </div>
        {displayTime && (
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <span className="flex items-center gap-1">
              <Icon name="schedule" className="text-base" />
              {displayTime}
            </span>
          </div>
        )}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {recipe.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
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
      className={`px-5 py-2 rounded-full font-semibold text-sm transition-colors whitespace-nowrap ${
        active
          ? 'bg-primary text-white'
          : 'bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300'
      }`}
    >
      {label}
    </button>
  );
};

interface RecipeBinderScreenProps {
  readonly className?: string;
}

export const RecipeBinderScreen: React.FC<RecipeBinderScreenProps> = ({
  className = '',
}) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const recipeId = searchParams.get('recipe');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  const filters = ['All', 'Favorites', 'Quick', 'Recent'];

  const { data: recipes, isLoading, error } = useRecipes();

  // Handle API errors with toast
  useEffect(() => {
    if (error) {
      toast.error('Failed to load recipes');
    }
  }, [error]);

  // Filter recipes client-side based on search query
  const filteredRecipes = recipes?.filter((recipe) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      recipe.title.toLowerCase().includes(query) ||
      (recipe.description?.toLowerCase().includes(query) ?? false) ||
      (recipe.tags?.some((tag) => tag.toLowerCase().includes(query)) ?? false)
    );
  });

  const handleRecipeClick = (id: number) => {
    setSearchParams({ recipe: String(id) });
  };

  const handleCloseModal = () => {
    setSearchParams({});
  };

  return (
    <div
      className={`relative flex min-h-screen flex-col overflow-x-hidden bg-background-dark ${className}`}
    >
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background-dark/80 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <Icon name="restaurant_menu" className="text-primary text-3xl" />
              <h1 className="text-xl font-bold tracking-tight text-slate-100">
                Recipe Binder
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <button className="flex items-center justify-center p-2 rounded-lg hover:bg-slate-800 transition-colors">
                <Icon name="account_circle" className="text-slate-300" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Search */}
        <div className="mb-10 max-w-3xl mx-auto">
          <Input
            value={searchQuery}
            onChange={setSearchQuery}
            icon="auto_awesome"
            placeholder="Search your binder with natural language (e.g., 'Quick spicy chicken dinner')..."
            className="text-lg shadow-sm"
          />
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
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Sort by:
            </span>
            <button className="flex items-center gap-1 text-sm font-medium text-slate-300 hover:text-primary transition-colors">
              Recent <Icon name="expand_more" className="text-sm" />
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && (!filteredRecipes || filteredRecipes.length === 0) && (
          <div className="text-center py-12">
            <Icon name="restaurant_menu" className="text-slate-600 text-5xl mb-4" />
            <h3 className="text-lg font-semibold text-slate-300 mb-2">
              {searchQuery ? 'No recipes found' : 'No recipes yet'}
            </h3>
            <p className="text-slate-500 mb-6">
              {searchQuery
                ? 'Try a different search term'
                : 'Import your first recipe to get started'}
            </p>
            {!searchQuery && (
              <Button icon="add" size="large">
                Add Recipe
              </Button>
            )}
          </div>
        )}

        {/* Recipe Grid */}
        {!isLoading && filteredRecipes && filteredRecipes.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredRecipes.map((recipe) => (
              <RecipeCardItem
                key={recipe.id}
                recipe={recipe}
                onClick={() => handleRecipeClick(recipe.id)}
              />
            ))}
          </div>
        )}
      </main>

      {/* Floating Action Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <Button
          icon="add"
          size="large"
          className="rounded-full px-6 shadow-lg hover:shadow-primary/30 hover:scale-105"
        >
          Add Recipe
        </Button>
      </div>

      {/* Recipe Detail Modal */}
      {recipeId && <RecipeDetailModal onClose={handleCloseModal} />}
    </div>
  );
};

export default RecipeBinderScreen;
