import { useState, useCallback } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import { arrayMove } from '@dnd-kit/sortable';
import { useBlocker } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useIngredientGroups, useBulkReplaceIngredients } from '@/hooks/useIngredients';
import { IngredientGroup } from './IngredientGroup';
import type {
  Ingredient,
  IngredientGroupWithIngredients,
} from '@/types/ingredient';

interface IngredientSectionProps {
  recipeId: number;
  className?: string;
}

// Generate temp IDs for new items (negative to avoid collision)
let tempIdCounter = -1;
const getTempId = () => tempIdCounter--;

export function IngredientSection({ recipeId, className }: IngredientSectionProps) {
  const { data: serverGroups, isLoading } = useIngredientGroups(recipeId);
  const bulkReplace = useBulkReplaceIngredients(recipeId);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [localGroups, setLocalGroups] = useState<IngredientGroupWithIngredients[]>([]);
  const [hasChanges, setHasChanges] = useState(false);

  // Block navigation on unsaved changes
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      hasChanges && currentLocation.pathname !== nextLocation.pathname
  );

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor)
  );

  // Enter edit mode - copy server data to local state
  const handleEnterEdit = useCallback(() => {
    setLocalGroups(serverGroups ?? []);
    setIsEditing(true);
    setHasChanges(false);
  }, [serverGroups]);

  // Cancel edit - warn if unsaved changes
  const handleCancel = useCallback(() => {
    if (hasChanges) {
      if (!confirm('Discard unsaved changes?')) return;
    }
    setIsEditing(false);
    setLocalGroups([]);
    setHasChanges(false);
  }, [hasChanges]);

  // Save changes - bulk PUT
  const handleSave = useCallback(async () => {
    // Transform local state to bulk request format
    const payload = {
      groups: localGroups.map((group) => ({
        id: group.id > 0 ? group.id : null,
        name: group.name,
        ingredients: group.ingredients.map((ing, ingIndex) => ({
          id: ing.id > 0 ? ing.id : null,
          quantity: ing.quantity,
          unit: ing.unit,
          name: ing.name,
          preparation: ing.preparation,
          raw: ing.raw,
          display_order: ingIndex,
        })),
      })),
    };

    await bulkReplace.mutateAsync(payload);
    setIsEditing(false);
    setHasChanges(false);
  }, [localGroups, bulkReplace]);

  // Group CRUD
  const handleAddGroup = useCallback(() => {
    const newGroup: IngredientGroupWithIngredients = {
      id: getTempId(),
      recipe_id: recipeId,
      name: `Group ${localGroups.length + 1}`,
      ingredients: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setLocalGroups([...localGroups, newGroup]);
    setHasChanges(true);
  }, [localGroups, recipeId]);

  const handleUpdateGroup = useCallback((groupId: number, name: string) => {
    setLocalGroups((groups) =>
      groups.map((g) => (g.id === groupId ? { ...g, name } : g))
    );
    setHasChanges(true);
  }, []);

  const handleDeleteGroup = useCallback((groupId: number) => {
    setLocalGroups((groups) => groups.filter((g) => g.id !== groupId));
    setHasChanges(true);
  }, []);

  // Ingredient CRUD
  const handleAddIngredient = useCallback((groupId: number) => {
    const newIngredient: Ingredient = {
      id: getTempId(),
      group_id: groupId,
      quantity: null,
      unit: null,
      name: '',
      preparation: null,
      raw: '',
      display_order: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setLocalGroups((groups) =>
      groups.map((g) =>
        g.id === groupId
          ? { ...g, ingredients: [...g.ingredients, newIngredient] }
          : g
      )
    );
    setHasChanges(true);
  }, []);

  const handleUpdateIngredient = useCallback((ingredient: Ingredient) => {
    setLocalGroups((groups) =>
      groups.map((g) =>
        g.id === ingredient.group_id
          ? {
              ...g,
              ingredients: g.ingredients.map((i) =>
                i.id === ingredient.id ? ingredient : i
              ),
            }
          : g
      )
    );
    setHasChanges(true);
  }, []);

  const handleDeleteIngredient = useCallback(
    (groupId: number, ingredientId: number) => {
      setLocalGroups((groups) =>
        groups.map((g) =>
          g.id === groupId
            ? {
                ...g,
                ingredients: g.ingredients.filter((i) => i.id !== ingredientId),
              }
            : g
        )
      );
      setHasChanges(true);
    },
    []
  );

  // DnD handler
  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      if (!over || active.id === over.id) return;

      // Find which group contains the dragged item and reorder
      setLocalGroups((groups) => {
        for (const group of groups) {
          const oldIndex = group.ingredients.findIndex(
            (i) => String(i.id) === active.id
          );
          const newIndex = group.ingredients.findIndex(
            (i) => String(i.id) === over.id
          );
          if (oldIndex !== -1 && newIndex !== -1) {
            const newIngredients = arrayMove(group.ingredients, oldIndex, newIndex);
            return groups.map((g) =>
              g.id === group.id ? { ...g, ingredients: newIngredients } : g
            );
          }
        }
        return groups;
      });
      setHasChanges(true);
    },
    []
  );

  // Determine display data
  const displayGroups = isEditing ? localGroups : serverGroups ?? [];
  const isSingleGroup = displayGroups.length <= 1;

  if (isLoading) {
    return <div className="text-slate-400">Loading ingredients...</div>;
  }

  return (
    <div className={cn('relative', className)}>
      {/* Header with Edit/Cancel/Save buttons */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">Ingredients</h2>

        {/* Edit button - HIDDEN on mobile (md:flex) */}
        {!isEditing ? (
          <button
            onClick={handleEnterEdit}
            className="hidden md:flex items-center gap-2 px-4 py-2 bg-primary text-white rounded hover:bg-primary/90"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-surface-dark text-slate-200 rounded hover:bg-surface-dark/80"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={bulkReplace.isPending}
              className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 disabled:opacity-50"
            >
              {bulkReplace.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>

      {/* Unsaved changes warning dialog */}
      {blocker.state === 'blocked' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface-dark p-6 rounded-lg max-w-sm">
            <p className="text-white mb-4">Discard unsaved changes?</p>
            <div className="flex gap-4 justify-end">
              <button
                onClick={() => blocker.reset()}
                className="px-4 py-2 text-slate-400 hover:text-white"
              >
                Stay
              </button>
              <button
                onClick={() => blocker.proceed()}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main content with optional DndContext */}
      {isEditing ? (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          {displayGroups.map((group) => (
            <IngredientGroup
              key={group.id}
              group={group}
              isEditing={isEditing}
              isSingleGroup={isSingleGroup}
              onUpdateGroup={handleUpdateGroup}
              onDeleteGroup={handleDeleteGroup}
              onAddIngredient={handleAddIngredient}
              onUpdateIngredient={handleUpdateIngredient}
              onDeleteIngredient={handleDeleteIngredient}
            />
          ))}
        </DndContext>
      ) : (
        displayGroups.map((group) => (
          <IngredientGroup
            key={group.id}
            group={group}
            isEditing={false}
            isSingleGroup={isSingleGroup}
          />
        ))
      )}

      {/* Add Group button - only in edit mode */}
      {isEditing && (
        <button
          onClick={handleAddGroup}
          className="mt-4 text-sm text-primary hover:text-primary/80"
        >
          + Add Group
        </button>
      )}
    </div>
  );
}
