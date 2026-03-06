// Types matching backend schemas from src/eat_it/schemas/ingredient.py

export interface Ingredient {
  id: number;
  group_id: number;
  quantity: number | null;
  unit: string | null;
  name: string;
  preparation: string | null;
  raw: string;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface IngredientGroup {
  id: number;
  recipe_id: number;
  name: string | null;
  created_at: string;
  updated_at: string;
}

export interface IngredientGroupWithIngredients extends IngredientGroup {
  ingredients: Ingredient[];
}

// Bulk operation payload types (for PUT request)
export interface IngredientBulkItem {
  id: number | null; // null for new ingredients
  quantity: number | null;
  unit: string | null;
  name: string;
  preparation: string | null;
  raw: string;
  display_order: number;
}

export interface IngredientGroupBulkItem {
  id: number | null; // null for new groups
  name: string | null;
  ingredients: IngredientBulkItem[];
}

export interface IngredientsBulkRequest {
  groups: IngredientGroupBulkItem[];
}

export interface IngredientsBulkResponse {
  groups: IngredientGroupWithIngredients[];
}
