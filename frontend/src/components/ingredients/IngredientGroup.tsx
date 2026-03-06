import { useState } from 'react';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { cn } from '@/lib/utils';
import { SortableIngredientRow } from './SortableIngredientRow';
import { IngredientRow } from './IngredientRow';
import type { Ingredient, IngredientGroupWithIngredients } from '@/types/ingredient';

interface IngredientGroupProps {
  group: IngredientGroupWithIngredients;
  isEditing: boolean;
  isSingleGroup: boolean;
  onUpdateGroup?: (groupId: number, name: string) => void;
  onDeleteGroup?: (groupId: number) => void;
  onAddIngredient?: (groupId: number) => void;
  onUpdateIngredient?: (ingredient: Ingredient) => void;
  onDeleteIngredient?: (groupId: number, ingredientId: number) => void;
}

export function IngredientGroup({
  group,
  isEditing,
  isSingleGroup,
  onUpdateGroup,
  onDeleteGroup,
  onAddIngredient,
  onUpdateIngredient,
  onDeleteIngredient,
}: IngredientGroupProps) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(group.name ?? '');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleRenameSubmit = () => {
    onUpdateGroup?.(group.id, renameValue);
    setIsRenaming(false);
  };

  const handleDeleteConfirm = () => {
    onDeleteGroup?.(group.id);
    setShowDeleteConfirm(false);
  };

  // In edit mode with sortable
  const ingredientIds = group.ingredients.map((i) => String(i.id));

  return (
    <div className="mb-6">
      {/* Group header - ONLY show if multiple groups */}
      {!isSingleGroup && (
        <div className="flex items-center gap-2 mb-3">
          {isRenaming && isEditing ? (
            <input
              type="text"
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onBlur={handleRenameSubmit}
              onKeyDown={(e) => e.key === 'Enter' && handleRenameSubmit()}
              className="px-2 py-1 bg-surface-dark rounded text-slate-200"
              autoFocus
            />
          ) : (
            <h3
              className={cn(
                'text-lg font-semibold text-white',
                isEditing && 'cursor-pointer hover:text-primary'
              )}
              onClick={() => isEditing && setIsRenaming(true)}
            >
              {group.name || 'Unnamed Group'}
            </h3>
          )}
          {isEditing && (
            <>
              <button
                onClick={() => setIsRenaming(true)}
                className="text-slate-400 hover:text-white text-sm"
              >
                Rename
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="text-red-400 hover:text-red-300 text-sm"
              >
                Delete
              </button>
            </>
          )}
        </div>
      )}

      {/* Delete confirmation dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface-dark p-6 rounded-lg max-w-sm">
            <p className="text-white mb-4">
              Delete group &quot;{group.name}&quot; and its{' '}
              {group.ingredients.length} ingredient(s)?
            </p>
            <div className="flex gap-4 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ingredients list */}
      {isEditing ? (
        <SortableContext items={ingredientIds} strategy={verticalListSortingStrategy}>
          <div className="space-y-2">
            {group.ingredients.map((ingredient) => (
              <SortableIngredientRow
                key={ingredient.id}
                id={String(ingredient.id)}
                ingredient={ingredient}
                isEditing={isEditing}
                onUpdate={onUpdateIngredient}
                onDelete={() => onDeleteIngredient?.(group.id, ingredient.id)}
              />
            ))}
          </div>
        </SortableContext>
      ) : (
        <div className="space-y-2">
          {group.ingredients.map((ingredient) => (
            <IngredientRow
              key={ingredient.id}
              ingredient={ingredient}
              isEditing={false}
            />
          ))}
        </div>
      )}

      {/* Add ingredient button - only in edit mode */}
      {isEditing && (
        <button
          onClick={() => onAddIngredient?.(group.id)}
          className="mt-3 text-sm text-primary hover:text-primary/80"
        >
          + Add Ingredient
        </button>
      )}
    </div>
  );
}
