/**
 * TypeScript types for shopping list data.
 * Matches backend schemas from src/eat_it/schemas/shopping_list.py
 */

export interface ShoppingListItem {
  id: number;
  shopping_list_id: number;
  name: string;
  quantity: number | null;
  unit: string | null;
  section_id: number | null;
  checked: boolean;
  display_order: number | null;
  created_at: string;
  updated_at: string;
}

export interface ShoppingList {
  id: number;
  name: string;
  share_token: string | null;
  expires_at: string | null;
  items: ShoppingListItem[];
  created_at: string;
  updated_at: string;
}

export interface ShoppingListSummary {
  id: number;
  name: string;
  share_token: string | null;
  expires_at: string | null;
  items: ShoppingListItem[];
  created_at: string;
  updated_at: string;
}

export interface ShoppingListsResponse {
  data: ShoppingListSummary[];
  count: number;
}

export interface ShoppingListItemCreate {
  name: string;
  quantity?: number | null;
  unit?: string | null;
  section_id?: number | null;
  display_order?: number | null;
  checked?: boolean;
}

export interface ShoppingListItemUpdate {
  name?: string;
  quantity?: number | null;
  unit?: string | null;
  section_id?: number | null;
  display_order?: number | null;
  checked?: boolean;
}

export interface ShoppingListCreate {
  name: string;
  recipe_ids?: number[];
}

export interface ShoppingListUpdate {
  name?: string;
}

export interface ShoppingListGenerate {
  name: string;
  recipe_ids: number[];
}

export interface StoreSection {
  id: number;
  name: string;
  sort_order: number;
  is_default: boolean;
}

export interface StoreSectionsResponse {
  data: StoreSection[];
  count: number;
}
