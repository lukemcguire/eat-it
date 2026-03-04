import React from 'react';
import { useRecipeBinder } from '../../hooks';
import { type RecipeCard } from '../../data/mockData';
import { Icon, Button, Input } from '../ui';

interface RecipeCardProps {
  readonly recipe: RecipeCard;
  readonly onToggleFavorite: () => void;
}

const RecipeCardItem: React.FC<RecipeCardProps> = ({
  recipe,
  onToggleFavorite,
}) => {
  const difficultyColor = {
    Easy: 'text-green-400',
    Medium: 'text-yellow-400',
    Hard: 'text-red-400',
  };

  return (
    <div className="group relative flex flex-col bg-white dark:bg-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 hover:shadow-xl transition-all cursor-pointer">
      {/* Image */}
      <div className="aspect-[4/3] overflow-hidden">
        <div
          className="w-full h-full bg-slate-200 dark:bg-slate-800 bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
          style={{ backgroundImage: `url('${recipe.image}')` }}
          role="img"
          aria-label={recipe.title}
        />
      </div>

      {/* Content */}
      <div className="p-5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg leading-tight group-hover:text-primary transition-colors text-slate-900 dark:text-slate-100">
            {recipe.title}
          </h3>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite();
            }}
            className="text-slate-400 hover:text-red-500 transition-colors"
          >
            <Icon
              name="favorite"
              filled={recipe.isFavorite}
              className={recipe.isFavorite ? 'text-primary' : ''}
            />
          </button>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <span className="flex items-center gap-1">
            <Icon name="schedule" className="text-base" />
            {recipe.time}
          </span>
          <span className={`flex items-center gap-1 ${difficultyColor[recipe.difficulty]}`}>
            <Icon name="bar_chart" className="text-base" />
            {recipe.difficulty}
          </span>
        </div>
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
        <Button icon="add" size="large" className="rounded-full px-6 shadow-lg hover:shadow-primary/30 hover:scale-105">
          Add Recipe
        </Button>
      </div>
    </div>
  );
};

export default RecipeBinderScreen;
