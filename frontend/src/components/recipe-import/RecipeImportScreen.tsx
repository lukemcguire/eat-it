import React from 'react';
import { useRecipeImport } from '../../hooks';
import { Icon, Button, Input, Tag, Card } from '../ui';

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
  readonly quantity: string;
}

const IngredientRow: React.FC<IngredientRowProps> = ({ name, quantity }) => {
  return (
    <li className="flex justify-between text-sm">
      <span className="text-slate-300">{name}</span>
      <span className="font-medium text-slate-200">{quantity}</span>
    </li>
  );
};

interface RecipeImportScreenProps {
  readonly className?: string;
}

export const RecipeImportScreen: React.FC<RecipeImportScreenProps> = ({
  className = '',
}) => {
  const {
    url,
    setUrl,
    recipe,
    isLoaded,
    fetchRecipe,
    saveRecipe,
    discardRecipe,
  } = useRecipeImport();

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
          <button className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors">
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
                Paste any recipe URL below to automatically extract ingredients and instructions.
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
              />
              <Button icon="bolt" size="large" onClick={fetchRecipe}>
                Fetch Recipe
              </Button>
            </div>
          </Card>

          {/* Preview Section */}
          {isLoaded && recipe && (
            <section className="flex flex-col gap-6">
              <div className="flex items-center justify-between px-2">
                <h2 className="text-slate-100 text-2xl font-bold">
                  Preview Details
                </h2>
                <Tag variant="outline">Ready to Save</Tag>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-8 flex flex-col gap-6">
                  {/* Hero Preview */}
                  <div className="relative h-64 w-full rounded-2xl overflow-hidden group">
                    <img
                      src={recipe.heroImage}
                      alt={recipe.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900/80 to-transparent" />
                    <div className="absolute bottom-6 left-6 right-6">
                      <h3 className="text-white text-2xl font-bold">
                        {recipe.title}
                      </h3>
                      <p className="text-slate-200 text-sm mt-1">
                        Found on &quot;{recipe.source}&quot;
                      </p>
                    </div>
                    <button className="absolute top-4 right-4 bg-white/20 backdrop-blur-md hover:bg-white/30 text-white p-2 rounded-lg transition-colors">
                      <Icon name="edit" />
                    </button>
                  </div>

                  {/* Instructions */}
                  <Card className="p-8 border-slate-800/50">
                    <div className="flex items-center justify-between mb-6">
                      <h4 className="text-lg font-bold flex items-center gap-2 text-slate-100">
                        <Icon name="format_list_numbered" className="text-primary" />
                        Instructions
                      </h4>
                      <button className="text-primary text-sm font-semibold hover:underline">
                        Edit Steps
                      </button>
                    </div>
                    <div className="space-y-4">
                      {recipe.steps.map((step) => (
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
                          {recipe.time}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-slate-400 text-xs uppercase font-bold tracking-wider">
                          Servings
                        </span>
                        <span className="font-bold text-slate-100">
                          {recipe.servings}
                        </span>
                      </div>
                    </div>
                  </Card>

                  {/* Ingredients */}
                  <Card className="p-8 border-slate-800/50">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-3 mb-6">
                      <h4 className="font-bold flex items-center gap-2 text-slate-100">
                        <Icon name="shopping_basket" className="text-primary text-xl" />
                        Ingredients
                      </h4>
                      <span className="text-xs text-slate-500">
                        {recipe.ingredients.length} items
                      </span>
                    </div>
                    <ul className="space-y-3">
                      {recipe.ingredients.map((ing, idx) => (
                        <IngredientRow
                          key={idx}
                          name={ing.name}
                          quantity={ing.quantity}
                        />
                      ))}
                    </ul>
                    <button className="mt-4 w-full py-2 border border-dashed border-slate-700 rounded-lg text-slate-400 text-sm hover:border-primary hover:text-primary transition-colors">
                      + Add Ingredient
                    </button>
                  </Card>
                </div>
              </div>

              {/* Final Actions */}
              <div className="flex items-center justify-end gap-4 pt-6 border-t border-slate-800">
                <Button variant="secondary" onClick={discardRecipe}>
                  Discard
                </Button>
                <Button icon="check" size="large" onClick={saveRecipe}>
                  Confirm &amp; Save Recipe
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
