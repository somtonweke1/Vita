/**
 * Main Application Component
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from '@/pages/Dashboard';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import '@/styles/globals.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          {/* Additional routes would go here:
          <Route path="/health-profile" element={<HealthProfile />} />
          <Route path="/programs" element={<Programs />} />
          <Route path="/wearables" element={<Wearables />} />
          <Route path="/financial" element={<Financial />} />
          */}
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;