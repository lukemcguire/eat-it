export interface Recipe {
  id: number;
  title: string;
  description: string | null;
  instructions: string;
  prep_time: string | null;
  cook_time: string | null;
  servings: string | null;
  source_url: string | null;
  image_url: string | null;
  tags: string[] | null;
  rating: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecipeCreate {
  title: string;
  description?: string | null;
  instructions: string;
  prep_time?: string | null;
  cook_time?: string | null;
  servings?: string | null;
  source_url?: string | null;
  image_url?: string | null;
  tags?: string[] | null;
}

export type RecipeUpdate = Partial<RecipeCreate>;

export interface RecipeRatingUpdate {
  rating: number | null;
}

export interface RecipeNotesUpdate {
  notes: string | null;
}

export interface ParseResponse {
  success: boolean;
  data?: Record<string, unknown>;
  error?: {
    code: string;
    message: string;
    suggested_action: string;
  };
  duplicate_warning?: {
    existing_recipe: Recipe;
  };
}
