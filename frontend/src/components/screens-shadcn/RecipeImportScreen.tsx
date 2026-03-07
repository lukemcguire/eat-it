import React from "react";
import { useRecipeImport } from "@/hooks";
import {
  Button,
  Card,
  Input,
  Badge,
} from "@/components/shadcn";
import { cn } from "@/lib/utils";

interface ImportStepProps {
  readonly number: number;
  readonly description: string;
}

const ImportStep: React.FC<ImportStepProps> = ({ number, description }) => {
  return (
    <div className="flex gap-4">
      <span className="flex-none w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center mt-1">
        {number}
      </span>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
};

interface RecipeImportScreenProps {
  readonly className?: string;
}

export const RecipeImportScreen: React.FC<RecipeImportScreenProps> = ({
  className = "",
}) => {
  const {
    url,
    setUrl,
    parsedRecipe: recipe,
    parseError,
    isParsing,
    isSaving,
    parseRecipe,
    saveRecipe,
    discardRecipe,
    duplicateWarning,
  } = useRecipeImport();

  return (
    <div
      className={cn(
        "relative flex h-auto min-h-screen w-full flex-col bg-background overflow-x-hidden",
        className
      )}
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border/60 px-6 md:px-20 py-4 bg-card/40 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <span className="material-symbols-outlined text-3xl">restaurant_menu</span>
          </div>
          <h2 className="text-xl font-extrabold leading-tight tracking-tight">
            Recipe Importer
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon">
            <span className="material-symbols-outlined text-xl">close</span>
          </Button>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center">
        <div className="layout-content-container flex flex-col w-full max-w-4xl px-6 py-10 gap-8">
          {/* URL Input Section */}
          <Card className="p-8 shadow-sm">
            <div className="space-y-2">
              <h1 className="text-3xl font-extrabold leading-tight tracking-tight">
                Import New Recipe
              </h1>
              <p className="text-muted-foreground text-base">
                Paste any recipe URL below to automatically extract ingredients and
                instructions.
              </p>
            </div>
            <div className="flex flex-col md:flex-row gap-4 mt-6">
              <div className="flex-1 relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
                  link
                </span>
                <Input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://cooking-site.com/delicious-pasta"
                  type="url"
                  className="pl-12"
                />
              </div>
              <Button size="lg" onClick={parseRecipe} disabled={isParsing}>
                <span className="material-symbols-outlined">bolt</span>
                {isParsing ? 'Fetching...' : 'Fetch Recipe'}
              </Button>
            </div>
          </Card>

          {/* Error Message */}
          {parseError && (
            <Card className="p-6 border-destructive bg-destructive/10">
              <p className="text-destructive font-medium">{parseError}</p>
            </Card>
          )}

          {/* Duplicate Warning */}
          {duplicateWarning && (
            <Card className="p-6 border-warning bg-warning/10">
              <p className="text-warning font-medium">
                This recipe may be a duplicate of &quot;{duplicateWarning.existing_recipe.title}&quot;
              </p>
            </Card>
          )}

          {/* Preview Section */}
          {recipe && (
            <section className="flex flex-col gap-6">
              <div className="flex items-center justify-between px-2">
                <h2 className="text-2xl font-bold">Preview Details</h2>
                <Badge variant="outline">Ready to Save</Badge>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                  {/* Hero Preview */}
                  {recipe.image_url && (
                    <div className="relative h-64 w-full rounded-2xl overflow-hidden group">
                      <img
                        src={recipe.image_url}
                        alt={recipe.title}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-background/80 to-transparent" />
                      <div className="absolute bottom-6 left-6 right-6">
                        <h3 className="text-white text-2xl font-bold">
                          {recipe.title}
                        </h3>
                        {recipe.source_url && (
                          <p className="text-white/80 text-sm mt-1">
                            Found on &quot;{new URL(recipe.source_url).hostname}&quot;
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Title (shown if no image) */}
                  {!recipe.image_url && (
                    <Card className="p-6">
                      <h3 className="text-2xl font-bold">{recipe.title}</h3>
                      {recipe.description && (
                        <p className="text-muted-foreground mt-2">{recipe.description}</p>
                      )}
                    </Card>
                  )}

                  {/* Instructions */}
                  {recipe.instructions && (
                    <Card className="p-8">
                      <div className="flex items-center justify-between mb-6">
                        <h4 className="text-lg font-bold flex items-center gap-2">
                          <span className="material-symbols-outlined text-primary">
                            format_list_numbered
                          </span>
                          Instructions
                        </h4>
                      </div>
                      <div className="prose prose-sm max-w-none">
                        {recipe.instructions.split(/\n\n?/).map((step, idx) => (
                          <ImportStep
                            key={idx}
                            number={idx + 1}
                            description={step}
                          />
                        ))}
                      </div>
                    </Card>
                  )}
                </div>

                {/* Sidebar */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                  {/* Quick Info */}
                  <Card className="p-8">
                    <div className="flex flex-col space-y-6">
                      {(recipe.prep_time || recipe.cook_time) && (
                        <div className="flex flex-col">
                          <span className="text-muted-foreground text-xs uppercase font-bold tracking-wider">
                            Time
                          </span>
                          <span className="font-bold">
                            {[recipe.prep_time, recipe.cook_time].filter(Boolean).join(' / ')}
                          </span>
                        </div>
                      )}
                      {recipe.servings && (
                        <div className="flex flex-col">
                          <span className="text-muted-foreground text-xs uppercase font-bold tracking-wider">
                            Servings
                          </span>
                          <span className="font-bold">{recipe.servings}</span>
                        </div>
                      )}
                    </div>
                  </Card>

                  {/* Ingredients */}
                  {recipe.ingredients && recipe.ingredients.length > 0 && (
                    <Card className="p-8">
                      <div className="flex items-center justify-between border-b border-border pb-3 mb-6">
                        <h4 className="font-bold flex items-center gap-2">
                          <span className="material-symbols-outlined text-primary text-xl">
                            shopping_basket
                          </span>
                          Ingredients
                        </h4>
                        <span className="text-xs text-muted-foreground">
                          {recipe.ingredients.length} items
                        </span>
                      </div>
                      <ul className="space-y-3">
                        {recipe.ingredients.map((ing, idx) => (
                          <li key={idx} className="text-sm text-muted-foreground">
                            {ing}
                          </li>
                        ))}
                      </ul>
                    </Card>
                  )}

                  {/* Tags */}
                  {recipe.tags && recipe.tags.length > 0 && (
                    <Card className="p-6">
                      <h4 className="font-bold mb-3">Tags</h4>
                      <div className="flex flex-wrap gap-2">
                        {recipe.tags.map((tag, idx) => (
                          <Badge key={idx} variant="secondary">{tag}</Badge>
                        ))}
                      </div>
                    </Card>
                  )}
                </div>
              </div>

              {/* Final Actions */}
              <div className="flex items-center justify-end gap-4 pt-6 border-t border-border">
                <Button variant="secondary" onClick={discardRecipe} disabled={isSaving}>
                  Discard
                </Button>
                <Button size="lg" onClick={saveRecipe} disabled={isSaving}>
                  {isSaving ? 'Saving...' : 'Confirm & Save Recipe'}
                </Button>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-border/50 flex justify-center text-muted-foreground text-sm">
        <div className="flex items-center gap-6">
          <a href="#" className="hover:text-primary transition-colors">
            Help Center
          </a>
          <span className="w-1 h-1 rounded-full bg-muted-foreground" />
          <a href="#" className="hover:text-primary transition-colors">
            Privacy Policy
          </a>
          <span className="w-1 h-1 rounded-full bg-muted-foreground" />
          <a href="#" className="hover:text-primary transition-colors">
            Terms of Service
          </a>
        </div>
      </footer>
    </div>
  );
};

export default RecipeImportScreen;
