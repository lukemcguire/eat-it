import React from "react";
import { recipeDetail } from "@/data/mockData";
import {
  Button,
  Card,
  CardContent,
  Badge,
  Avatar,
  AvatarImage,
  Separator,
  Table,
  TableBody,
  TableRow,
  TableCell,
} from "@/components/shadcn";
import { cn } from "@/lib/utils";

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
      <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full bg-primary text-primary-foreground font-bold transition-all shadow-md shadow-primary/20 group-hover:scale-110">
        {number}
      </div>
      <div className="flex flex-col gap-2 pt-1">
        <h3 className="text-lg font-bold">{title}</h3>
        <p className="text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </div>
  );
};

interface RecipeDetailScreenProps {
  readonly className?: string;
}

export const RecipeDetailScreen: React.FC<RecipeDetailScreenProps> = ({
  className = "",
}) => {
  return (
    <div
      className={cn(
        "relative flex h-auto min-h-screen w-full flex-col bg-background overflow-x-hidden",
        className
      )}
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border px-6 md:px-20 py-4 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <div className="text-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-3xl">restaurant_menu</span>
          </div>
          <h2 className="text-lg font-bold leading-tight tracking-tight">
            Recipe Detail
          </h2>
        </div>
        <div className="flex flex-1 justify-end gap-4">
          <Button variant="ghost" size="icon">
            <span className="material-symbols-outlined text-[20px]">share</span>
          </Button>
          <Button variant="ghost" size="icon">
            <span className="material-symbols-outlined text-[20px]">favorite</span>
          </Button>
          <Avatar>
            <AvatarImage src="https://lh3.googleusercontent.com/aida-public/AB6AXuBwqMyNdeUDRWNc9_eV0OMSgoTRxNe8wFZEWOzec0sOc1IHJVQiL1DsHa4JCcLJqXX7qFWF28GhVQ0BP2P5VzrssEZN1VIQsi-UA3QljPrjfWZo94vwCntkuYFewui8njIJPubNms23d4qS194K79xIkf4vvYH9ERvXyCcY6yRWqL0RfaTK9VP81xNKtgAugSOajC6ktUAk31Jjb5bAWD3BFMSx443IjGkkXYPpdC-t-ydbPrA3H67Vp9t9SBA7zZmy_vc-IzUBNaQ" />
          </Avatar>
        </div>
      </header>

      <main className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full px-4 md:px-10 py-8 gap-8">
        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Hero Image */}
          <div className="w-full aspect-square md:aspect-video lg:aspect-square rounded-xl overflow-hidden shadow-2xl relative group">
            <div className="absolute inset-0 bg-gradient-to-t from-background/60 to-transparent z-10" />
            <img
              src={recipeDetail.heroImage}
              alt={recipeDetail.title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div className="absolute bottom-6 left-6 z-20">
              <Badge>{recipeDetail.tag}</Badge>
            </div>
          </div>

          {/* Hero Content */}
          <div className="flex flex-col gap-6">
            <div className="space-y-2">
              <h1 className="text-4xl md:text-5xl font-black leading-tight">
                {recipeDetail.title}
              </h1>
              <p className="text-primary/70 text-lg">{recipeDetail.subtitle}</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardContent className="flex flex-col gap-1 p-4">
                  <span className="material-symbols-outlined text-primary mb-1">timer</span>
                  <p className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
                    Prep Time
                  </p>
                  <p className="text-xl font-bold">{recipeDetail.prepTime}</p>
                </CardContent>
              </Card>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardContent className="flex flex-col gap-1 p-4">
                  <span className="material-symbols-outlined text-primary mb-1">local_fire_department</span>
                  <p className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
                    Calories
                  </p>
                  <p className="text-xl font-bold">{recipeDetail.calories}</p>
                </CardContent>
              </Card>
              <Card className="hover:border-primary/50 transition-colors cursor-pointer">
                <CardContent className="flex flex-col gap-1 p-4">
                  <span className="material-symbols-outlined text-primary mb-1">group</span>
                  <p className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
                    Servings
                  </p>
                  <p className="text-xl font-bold">{recipeDetail.servings}</p>
                </CardContent>
              </Card>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button size="lg" className="flex-1">
                <span className="material-symbols-outlined">play_circle</span>
                Start Cooking Mode
              </Button>
              <Button variant="secondary" size="lg">
                <span className="material-symbols-outlined">list_alt</span>
                Add to List
              </Button>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12 mt-8">
          {/* Ingredients */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">Ingredients</h2>
              <Separator className="flex-1" />
            </div>
            <Card>
              <Table>
                <TableBody>
                  {recipeDetail.ingredients.map((ingredient, idx) => (
                    <TableRow
                      key={idx}
                      className="hover:bg-muted/50 transition-colors"
                    >
                      <TableCell className="font-medium">{ingredient.name}</TableCell>
                      <TableCell className="text-right text-muted-foreground">
                        {ingredient.quantity}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </div>

          {/* Instructions */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <h2 className="text-2xl font-bold tracking-tight">Instructions</h2>
              <Separator className="flex-1" />
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
      <footer className="border-t border-border mt-12 py-8 px-6 text-center">
        <p className="text-muted-foreground text-sm">
          © 2024 Nordic Kitchen Chronicles. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default RecipeDetailScreen;
