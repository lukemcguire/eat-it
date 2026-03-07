import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRecipeImport } from '../../hooks';
import { Icon, Button, Input, Tag, Card } from '../ui';
import { toast } from 'sonner';

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
      <p className="text-slate-300">{description}</p>
    </div>
  );
};

interface IngredientRowProps {
  readonly name: string;
  readonly quantity?: string;
}

const IngredientRow: React.FC<IngredientRowProps> = ({ name, quantity }) => {
  return (
    <li className="flex justify-between text-sm">
      <span className="text-slate-300">{name}</span>
      {quantity && (
        <span className="font-medium text-slate-200">{quantity}</span>
      )}
    </li>
  );
};

interface RecipeImportScreenProps {
  readonly className?: string;
}

export const RecipeImportScreen: React.FC<RecipeImportScreenProps> = ({
  className = '',
}) => {
  const navigate = useNavigate();
  const {
    url,
    setUrl,
    parsedRecipe,
    parseError,
    isParsing,
    isSaving,
    parseRecipe,
    saveRecipe,
    discardRecipe,
    duplicateWarning,
  } = useRecipeImport();

  // Handle save success
  const handleSaveRecipe = async () => {
    try {
      await saveRecipe();
      toast.success('Recipe saved successfully!');
      discardRecipe();
      navigate('/recipes');
    } catch {
      toast.error('Failed to save recipe');
    }
  };

  // Show parse error toast
  useEffect(() => {
    if (parseError) {
      toast.error(parseError);
    }
  }, [parseError]);

  // Split instructions into steps (simple line-based split)
  const steps = parsedRecipe?.instructions
    ? parsedRecipe.instructions
        .split(/\n+/)
        .filter((step) => step.trim())
        .map((description, index) => ({
          number: index + 1,
          description: description.trim(),
        }))
    : [];

  return (
    <div
      className={`relative flex h-auto min-h-screen w-full flex-col bg-background-dark overflow-x-hidden ${className}`}
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-slate-800/60 px-6 md:px-20 py-4 bg-charcoal-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Icon name="restaurant_menu" className="text-3xl" />
          </div>
          <h2 className="text-slate-100 text-xl font-extrabold leading-tight tracking-tight">
            Recipe Importer
          </h2>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => discardRecipe()}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
          >
            <Icon name="close" className="text-xl" />
          </button>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center">
        <div className="layout-content-container flex flex-col w-full max-w-4xl px-6 py-10 gap-8">
          {/* URL Input Section */}
          <Card className="p-8 shadow-sm border-slate-800/50">
            <div className="space-y-2">
              <h1 className="text-slate-100 text-3xl font-extrabold leading-tight tracking-tight">
                Import New Recipe
              </h1>
              <p className="text-slate-400 text-base">
                Paste any recipe URL below to automatically extract ingredients
                and instructions.
              </p>
            </div>
            <div className="flex flex-col md:flex-row gap-4 mt-6">
              <Input
                value={url}
                onChange={setUrl}
                icon="link"
                placeholder="https://cooking-site.com/delicious-pasta"
                type="url"
                className="flex-1"
                disabled={isParsing}
              />
              <Button
                icon="bolt"
                size="large"
                onClick={parseRecipe}
                disabled={isParsing || !url.trim()}
              >
                {isParsing ? 'Fetching...' : 'Fetch Recipe'}
              </Button>
            </div>
            {parseError && (
              <p className="mt-4 text-red-400 text-sm">{parseError}</p>
            )}
          </Card>

          {/* Preview Section */}
          {parsedRecipe && (
            <section className="flex flex-col gap-6">
              <div className="flex items-center justify-between px-2">
                <h2 className="text-slate-100 text-2xl font-bold">
                  Preview Details
                </h2>
                <Tag variant="outline">Ready to Save</Tag>
              </div>

              {/* Duplicate Warning */}
              {duplicateWarning && (
                <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-yellow-400">
                    <Icon name="warning" />
                    <span className="font-semibold">
                      Potential Duplicate Found
                    </span>
                  </div>
                  <p className="text-yellow-300 text-sm mt-2">
                    This recipe may be a duplicate of &quot;
                    {duplicateWarning.existing_recipe.title}&quot;. Consider
                    checking your binder before saving.
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                  {/* Hero Preview */}
                  <div className="relative h-64 w-full rounded-2xl overflow-hidden group">
                    {parsedRecipe.image_url ? (
                      <img
                        src={parsedRecipe.image_url}
                        alt={parsedRecipe.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-slate-800 flex items-center justify-center">
                        <Icon
                          name="restaurant_menu"
                          className="text-slate-600 text-6xl"
                        />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900/80 to-transparent" />
                    <div className="absolute bottom-6 left-6 right-6">
                      <h3 className="text-white text-2xl font-bold">
                        {parsedRecipe.title}
                      </h3>
                      {parsedRecipe.source_url && (
                        <p className="text-slate-200 text-sm mt-1">
                          Found on &quot;
                          {new URL(parsedRecipe.source_url).hostname}&quot;
                        </p>
                      )}
                    </div>
                    <button className="absolute top-4 right-4 bg-white/20 backdrop-blur-md hover:bg-white/30 text-white p-2 rounded-lg transition-colors">
                      <Icon name="edit" />
                    </button>
                  </div>

                  {/* Instructions */}
                  <Card className="p-8 border-slate-800/50">
                    <div className="flex items-center justify-between mb-6">
                      <h4 className="text-lg font-bold flex items-center gap-2 text-slate-100">
                        <Icon
                          name="format_list_numbered"
                          className="text-primary"
                        />
                        Instructions
                      </h4>
                      <button className="text-primary text-sm font-semibold hover:underline">
                        Edit Steps
                      </button>
                    </div>
                    <div className="space-y-4">
                      {steps.map((step) => (
                        <ImportStep
                          key={step.number}
                          number={step.number}
                          description={step.description}
                        />
                      ))}
                    </div>
                  </Card>
                </div>

                {/* Sidebar */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                  {/* Quick Info */}
                  <Card className="p-8 border-slate-800/50">
                    <div className="flex flex-col space-y-6">
                      <div className="flex flex-col">
                        <span className="text-slate-400 text-xs uppercase font-bold tracking-wider">
                          Time
                        </span>
                        <span className="font-bold text-slate-100">
                          {[
                            parsedRecipe.prep_time,
                            parsedRecipe.cook_time,
                          ]
                            .filter(Boolean)
                            .join(' + ') || 'Not specified'}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-slate-400 text-xs uppercase font-bold tracking-wider">
                          Servings
                        </span>
                        <span className="font-bold text-slate-100">
                          {parsedRecipe.servings || 'Not specified'}
                        </span>
                      </div>
                    </div>
                  </Card>

                  {/* Ingredients */}
                  <Card className="p-8 border-slate-800/50">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-3 mb-6">
                      <h4 className="font-bold flex items-center gap-2 text-slate-100">
                        <Icon
                          name="shopping_basket"
                          className="text-primary text-xl"
                        />
                        Ingredients
                      </h4>
                      <span className="text-xs text-slate-500">
                        {parsedRecipe.ingredients?.length || 0} items
                      </span>
                    </div>
                    {parsedRecipe.ingredients &&
                    parsedRecipe.ingredients.length > 0 ? (
                      <ul className="space-y-3">
                        {parsedRecipe.ingredients.map((ing, idx) => (
                          <IngredientRow key={idx} name={ing} />
                        ))}
                      </ul>
                    ) : (
                      <p className="text-slate-500 text-sm">
                        No ingredients found
                      </p>
                    )}
                    <button className="mt-4 w-full py-2 border border-dashed border-slate-700 rounded-lg text-slate-400 text-sm hover:border-primary hover:text-primary transition-colors">
                      + Add Ingredient
                    </button>
                  </Card>

                  {/* Tags */}
                  {parsedRecipe.tags && parsedRecipe.tags.length > 0 && (
                    <Card className="p-6 border-slate-800/50">
                      <h4 className="font-bold text-slate-100 mb-3">Tags</h4>
                      <div className="flex flex-wrap gap-2">
                        {parsedRecipe.tags.map((tag) => (
                          <Tag key={tag} variant="outline">
                            {tag}
                          </Tag>
                        ))}
                      </div>
                    </Card>
                  )}
                </div>
              </div>

              {/* Final Actions */}
              <div className="flex items-center justify-end gap-4 pt-6 border-t border-slate-800">
                <Button variant="secondary" onClick={discardRecipe}>
                  Discard
                </Button>
                <Button
                  icon="check"
                  size="large"
                  onClick={handleSaveRecipe}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Confirm & Save Recipe'}
                </Button>
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-800/50 flex justify-center text-slate-500 text-sm">
        <div className="flex items-center gap-6">
          <a href="#" className="hover:text-primary transition-colors">
            Help Center
          </a>
          <span className="w-1 h-1 rounded-full bg-slate-700" />
          <a href="#" className="hover:text-primary transition-colors">
            Privacy Policy
          </a>
          <span className="w-1 h-1 rounded-full bg-slate-700" />
          <a href="#" className="hover:text-primary transition-colors">
            Terms of Service
          </a>
        </div>
      </footer>
    </div>
  );
};

export default RecipeImportScreen;
