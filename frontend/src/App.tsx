import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { AppLayout } from '@/components/layout/AppLayout';
import { RecipeBinderScreen } from '@/components/recipe-binder/RecipeBinderScreen';
import { ShoppingListScreen } from '@/components/shopping/ShoppingListScreen';
import { SearchScreen } from '@/components/screens/SearchScreen';
import { RecipeImportScreen } from '@/components/recipe-import/RecipeImportScreen';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="bottom-center" richColors />
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Navigate to="/recipes" replace />} />
            <Route path="/recipes" element={<RecipeBinderScreen />} />
            <Route path="/shopping/:id?" element={<ShoppingListScreen />} />
            <Route path="/search" element={<SearchScreen />} />
            <Route path="/import" element={<RecipeImportScreen />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
