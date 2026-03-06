import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import type { Ingredient } from '@/types/ingredient';

interface IngredientRowProps extends HTMLAttributes<HTMLDivElement> {
  ingredient: Ingredient;
  isEditing?: boolean;
  onUpdate?: (ingredient: Ingredient) => void;
  onDelete?: () => void;
}

export const IngredientRow = forwardRef<HTMLDivElement, IngredientRowProps>(
  ({ ingredient, isEditing, onUpdate, onDelete, className, ...props }, ref) => {
    if (!isEditing) {
      // View mode: display quantity/unit and name
      const quantityDisplay = [
        ingredient.quantity,
        ingredient.unit,
      ]
        .filter(Boolean).join(' ')
        .trim();
      const formattedQty = quantityDisplay
        ? `${quantityDisplay} ${ingredient.name}`
        : ingredient.name;

      return (
        <div ref={ref} className={cn('flex items-center gap-3', className)} {...props}>
          <span className="text-slate-200">{formattedQty}</span>
          {ingredient.preparation && (
            <span className="text-slate-400 text-sm">
              , {ingredient.preparation}
            </span>
          )}
          {ingredient.raw && (
            <span className="text-slate-500 text-xs">{ingredient.raw}</span>
          )}
        </div>
      );
    }

    // Edit mode: show editable fields
    return (
      <div ref={ref} className={cn('flex items-center gap-2', className)} {...props}>
        <input
          type="number"
          value={ingredient.quantity ?? ''}
          onChange={(e) =>
            onUpdate?.({ ...ingredient, quantity: parseFloat(e.target.value) || null })
          }
          className="w-20 px-2 py-1 bg-surface-dark rounded"
          placeholder="Qty"
        />
        <input
          type="text"
          value={ingredient.unit ?? ''}
          onChange={(e) =>
            onUpdate?.({ ...ingredient, unit: e.target.value || null })
          }
          className="w-20 px-2 py-1 bg-surface-dark rounded"
          placeholder="Unit"
        />
        <input
          type="text"
          value={ingredient.name}
          onChange={(e) =>
            onUpdate?.({ ...ingredient, name: e.target.value })}
          className="w-40 px-2 py-1 bg-surface-dark rounded"
          placeholder="Name"
          required
        />
        <input
          type="text"
          value={ingredient.preparation ?? ''}
          onChange={(e) =>
            onUpdate?.({ ...ingredient, preparation: e.target.value || null })
          }
          className="w-20 px-2 py-1 bg-surface-dark rounded"
          placeholder="Prep (optional)"
        />
        {onDelete && (
          <button
            onClick={onDelete}
            className="text-red-400 hover:text-red-300 text-sm"
          >
            Delete
          </button>
        )}
      </div>
    );
  }
);

IngredientRow.displayName = 'IngredientRow';
