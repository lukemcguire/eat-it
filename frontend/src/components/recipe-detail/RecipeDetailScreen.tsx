import React from 'react';
import { useParams } from 'react-router-dom';
import { recipeDetail } from '../../data/mockData';
import { Icon, Button, Tag, StepNumber, Card } from '../ui';
import { IngredientSection } from '../ingredients';

interface InstructionStepProps {
  readonly number: number;
  readonly title: string;
  readonly description: string;
}

const InstructionStep: React.FC<InstructionStepProps> = ({
  number,
  title,
  description,
}) => {
  return (
    <div className="flex gap-6 group">
      <StepNumber number={number} />
      <div className="flex flex-col gap-2 pt-1">
        <h3 className="text-lg font-bold text-white">{title}</h3>
        <p className="text-slate-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
};

interface RecipeDetailScreenProps {
  readonly className?: string;
}

export const RecipeDetailScreen: React.FC<RecipeDetailScreenProps> = ({
  className = '',
}) => {
  const { id } = useParams<{ id: string }>();
  const recipeId = parseInt(id ?? '0', 10);

  return (
    <div
      className={`relative flex h-auto min-h-screen w-full flex-col bg-background-dark overflow-x-hidden ${className}`}
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border-dark px-6 md:px-20 py-4 bg-background-dark/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="text-primary flex items-center justify-center">
            <Icon name="restaurant_menu" className="text-3xl" />
          </div>
          <h2 className="text-lg font-bold leading-tight tracking-tight text-slate-100">
            Recipe Detail
          </h2>
        </div>
        <div className="flex flex-1 justify-end gap-4">
          <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-surface-dark text-slate-200 hover:text-primary hover:bg-primary/10 transition-all">
            <Icon name="share" className="text-[20px]" />
          </button>
          <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-surface-dark text-slate-200 hover:text-primary hover:bg-primary/10 transition-all">
            <Icon name="favorite" className="text-[20px]" />
          </button>
          <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border border-border-dark" />
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full px-4 md:px-10 py-8 gap-8">
        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Hero Image */}
          <div className="w-full aspect-square md:aspect-video lg:aspect-square rounded-xl overflow-hidden shadow-2xl relative group">
            <div className="absolute inset-0 bg-gradient-to-t from-background-dark/60 to-transparent z-10" />
            <img
              src={recipeDetail.heroImage}
              alt={recipeDetail.title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div className="absolute bottom-6 left-6 z-20">
              <Tag variant="primary">{recipeDetail.tag}</Tag>
            </div>
          </div>

          {/* Hero Content */}
          <div className="flex flex-col gap-6">
            <div className="space-y-2">
              <h1 className="text-4xl md:text-5xl font-black text-white leading-tight">
                {recipeDetail.title}
              </h1>
              <p className="text-nordic-blue text-lg">{recipeDetail.subtitle}</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              <Card hover>
                <div className="flex flex-col gap-1 p-4">
                  <Icon name="timer" className="text-primary mb-1" />
                  <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">
                    Prep Time
                  </p>
                  <p className="text-white text-xl font-bold">
                    {recipeDetail.prepTime}
                  </p>
                </div>
              </Card>
              <Card hover>
                <div className="flex flex-col gap-1 p-4">
                  <Icon name="local_fire_department" className="text-primary mb-1" />
                  <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">
                    Calories
                  </p>
                  <p className="text-white text-xl font-bold">
                    {recipeDetail.calories}
                  </p>
                </div>
              </Card>
              <Card hover>
                <div className="flex flex-col gap-1 p-4">
                  <Icon name="group" className="text-primary mb-1" />
                  <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">
                    Servings
                  </p>
                  <p className="text-white text-xl font-bold">
                    {recipeDetail.servings}
                  </p>
                </div>
              </Card>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button icon="play_circle" size="large" className="flex-1">
                Start Cooking Mode
              </Button>
              <Button icon="list_alt" variant="secondary" size="large">
                Add to List
              </Button>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mt-8">
          {/* Ingredients - managed by IngredientSection */}
          <div className="lg:col-span-1">
            <IngredientSection recipeId={recipeId} />
          </div>

          {/* Instructions */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold text-white tracking-tight">
                Instructions
              </h2>
              <div className="h-[2px] flex-1 bg-border-dark mt-1" />
            </div>
            <div className="flex flex-col gap-6">
              {recipeDetail.instructions.map((step) => (
                <InstructionStep
                  key={step.number}
                  number={step.number}
                  title={step.title}
                  description={step.description}
                />
              ))}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border-dark mt-12 py-8 px-6 text-center">
        <p className="text-slate-400 text-sm">
          © 2024 Nordic Kitchen Chronicles. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default RecipeDetailScreen;
