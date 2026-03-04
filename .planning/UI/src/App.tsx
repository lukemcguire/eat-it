import React, { useState } from 'react';
import {
  ShoppingListScreen,
  RecipeDetailScreen,
  RecipeBinderScreen,
  RecipeImportScreen,
} from './components';

type Screen = 'shopping' | 'detail' | 'binder' | 'import';

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>('binder');

  const screens: Record<Screen, React.ReactNode> = {
    shopping: <ShoppingListScreen />,
    detail: <RecipeDetailScreen />,
    binder: <RecipeBinderScreen />,
    import: <RecipeImportScreen />,
  };

  return (
    <div className="min-h-screen bg-background-dark font-display">
      {/* Development Navigation - Remove in production */}
      <nav className="fixed top-0 left-0 right-0 z-[100] bg-slate-900/90 backdrop-blur-md border-b border-slate-700 px-4 py-2 flex gap-2">
        {(['shopping', 'detail', 'binder', 'import'] as const).map((screen) => (
          <button
            key={screen}
            onClick={() => setCurrentScreen(screen)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
              currentScreen === screen
                ? 'bg-primary text-white'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {screen.charAt(0).toUpperCase() + screen.slice(1)}
          </button>
        ))}
      </nav>

      {/* Screen Content */}
      <div className="pt-14">
        {screens[currentScreen]}
      </div>
    </div>
  );
};

export default App;
