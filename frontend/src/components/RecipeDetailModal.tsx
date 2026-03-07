import { X, Clock, Users, Star, ExternalLink } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { useRecipe } from '@/hooks/useRecipes';
import { TouchButton } from '@/components/ui/TouchButton';
import { Tag } from '@/components/ui/Tag';

interface RecipeDetailModalProps {
  onClose: () => void;
}

export function RecipeDetailModal({ onClose }: RecipeDetailModalProps) {
  const [searchParams] = useSearchParams();
  const recipeIdParam = searchParams.get('recipe');
  const recipeId = recipeIdParam ? parseInt(recipeIdParam, 10) : null;

  const { data: recipe, isLoading, error } = useRecipe(recipeId ?? 0);

  const handleBackdropClick = () => {
    onClose();
  };

  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  if (!recipeId) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="recipe-modal-title"
    >
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto
          bg-[#0f172a] border border-[#2e4e6b] rounded-xl"
        onClick={handleContentClick}
      >
        {/* Close button */}
        <TouchButton
          variant="ghost"
          size="icon"
          className="absolute top-4 right-4 z-10"
          onClick={onClose}
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </TouchButton>

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#207fdf]" />
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="p-8 text-center">
            <p className="text-red-400">Failed to load recipe</p>
            <TouchButton
              variant="secondary"
              className="mt-4"
              onClick={onClose}
            >
              Close
            </TouchButton>
          </div>
        )}

        {/* Recipe content */}
        {recipe && (
          <div className="p-6">
            {/* Header */}
            <div className="mb-6">
              <h2
                id="recipe-modal-title"
                className="text-2xl font-bold text-white pr-10"
              >
                {recipe.title}
              </h2>
              {recipe.description && (
                <p className="mt-2 text-[#94a3b8]">{recipe.description}</p>
              )}
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap gap-4 mb-6 text-sm text-[#94a3b8]">
              {recipe.prep_time && (
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>Prep: {recipe.prep_time}</span>
                </div>
              )}
              {recipe.cook_time && (
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>Cook: {recipe.cook_time}</span>
                </div>
              )}
              {recipe.servings && (
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span>{recipe.servings}</span>
                </div>
              )}
              {recipe.rating && (
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span>{recipe.rating}/5</span>
                </div>
              )}
            </div>

            {/* Tags */}
            {recipe.tags && recipe.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {recipe.tags.map((tag) => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </div>
            )}

            {/* Instructions */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Instructions
              </h3>
              <div className="text-[#cbd5e1] whitespace-pre-wrap">
                {recipe.instructions}
              </div>
            </div>

            {/* Notes */}
            {recipe.notes && (
              <div className="mb-6 p-4 bg-[#1a2632] rounded-lg">
                <h3 className="text-lg font-semibold text-white mb-2">Notes</h3>
                <p className="text-[#94a3b8] whitespace-pre-wrap">
                  {recipe.notes}
                </p>
              </div>
            )}

            {/* Source link */}
            {recipe.source_url && (
              <a
                href={recipe.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-[#207fdf]
                  hover:text-[#60a5fa] transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                <span>View original source</span>
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
