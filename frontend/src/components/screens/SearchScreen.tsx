import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearch } from '@/hooks/useSearch';
import { useRecipes } from '@/hooks/useRecipes';
import { toast } from 'sonner';
import { Icon, Button, Input } from '@/components/ui';
import type { Recipe } from '@/types/recipe';

export const SearchScreen: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchTriggered, setSearchTriggered] = useState(false);
  const navigate = useNavigate();

  // Only search when triggered (manual, not live)
  const { data: results, isLoading, error } = useSearch(
    query,
    searchTriggered,
  );

  // Recent recipes for empty state
  const { data: recentRecipes } = useRecipes({ limit: 6 });

  // Handle errors
  React.useEffect(() => {
    if (error) {
      toast.error('Search failed');
    }
  }, [error]);

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      setSearchTriggered(true);
    }
  }, [query]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      }
    },
    [handleSearch],
  );

  const handleRecipeClick = useCallback(
    (id: number) => {
      navigate(`/recipes?recipe=${id}`);
    },
    [navigate],
  );

  const recipesToShow = searchTriggered ? results : recentRecipes;

  return (
    <div className="min-h-screen bg-[#0f1923] p-4 lg:p-6">
      {/* Search Bar */}
      <div className="max-w-3xl mx-auto mb-8">
        <div className="flex gap-2">
          <Input
            value={query}
            onChange={setQuery}
            onKeyDown={handleKeyDown}
            placeholder="Search recipes (e.g., 'quick chicken dinner')"
            icon="search"
            className="flex-1"
          />
          <Button
            icon="search"
            onClick={handleSearch}
            disabled={!query.trim()}
          >
            Search
          </Button>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto">
        {isLoading ? (
          <div className="text-center text-slate-400 py-12">Searching...</div>
        ) : (
          <>
            {/* Header */}
            {searchTriggered && (
              <h2 className="text-xl font-bold text-white mb-4">
                {(results?.length ?? 0)} result
                {(results?.length ?? 0) !== 1 ? 's' : ''} for &quot;{query}
                &quot;
              </h2>
            )}

            {!searchTriggered && (
              <h2 className="text-xl font-bold text-white mb-4">
                Recent Recipes
              </h2>
            )}

            {/* Recipe Grid - reuse pattern from RecipeBinderScreen */}
            {recipesToShow && recipesToShow.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {recipesToShow.map((recipe: Recipe) => (
                  <div
                    key={recipe.id}
                    onClick={() => handleRecipeClick(recipe.id)}
                    className="cursor-pointer group"
                  >
                    <div className="bg-slate-900 rounded-xl overflow-hidden border border-slate-800 hover:shadow-xl transition-all">
                      <div className="aspect-[4/3] bg-slate-800">
                        {recipe.image_url ? (
                          <img
                            src={recipe.image_url}
                            alt={recipe.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Icon
                              name="restaurant"
                              className="text-slate-600 text-4xl"
                            />
                          </div>
                        )}
                      </div>
                      <div className="p-4">
                        <h3 className="font-bold text-white group-hover:text-[#207fdf] transition-colors">
                          {recipe.title}
                        </h3>
                        {recipe.description && (
                          <p className="text-slate-400 text-sm mt-1 line-clamp-2">
                            {recipe.description}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : searchTriggered ? (
              <div className="text-center py-12">
                <Icon name="search_off" className="text-slate-600 text-5xl mb-4" />
                <p className="text-slate-400 text-lg">
                  No recipes found for &quot;{query}&quot;
                </p>
                <p className="text-slate-500 text-sm mt-2">
                  Try a different search term or browse your recipe binder
                </p>
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
};

export default SearchScreen;
