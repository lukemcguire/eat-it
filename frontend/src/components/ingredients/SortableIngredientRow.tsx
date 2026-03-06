import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { cn } from '@/lib/utils';
import { DragHandle } from './DragHandle';
import { IngredientRow } from './IngredientRow';
import type { Ingredient } from '@/types/ingredient';

interface SortableIngredientRowProps {
  id: string;
  ingredient: Ingredient;
  isEditing?: boolean;
  onUpdate?: (ingredient: Ingredient) => void;
  onDelete?: () => void;
  className?: string;
}

export function SortableIngredientRow({
  id,
  ingredient,
  isEditing,
  onUpdate,
  onDelete,
  className,
}: SortableIngredientRowProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn('flex items-center', className)}
      {...attributes}
    >
      {isEditing && <DragHandle {...listeners} />}
      <IngredientRow
        ingredient={ingredient}
        isEditing={isEditing}
        onUpdate={onUpdate}
        onDelete={onDelete}
      />
    </div>
  );
}
