import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background-dark text-white">
        <h1>Eat It</h1>
        <p>Recipe management app</p>
      </div>
    </QueryClientProvider>
  );
}

export default App;
