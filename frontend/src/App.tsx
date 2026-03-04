import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from '@/components/layout/AppLayout';

// Placeholder screen components
const RecipeBinder = () => (
  <div className="text-white">Recipe Binder</div>
);
const ShoppingList = () => (
  <div className="text-white">Shopping List</div>
);
const Search = () => (
  <div className="text-white">Search</div>
);
const RecipeImport = () => (
  <div className="text-white">Recipe Import</div>
);

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
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<RecipeBinder />} />
            <Route path="/shopping" element={<ShoppingList />} />
            <Route path="/search" element={<Search />} />
            <Route path="/import" element={<RecipeImport />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
