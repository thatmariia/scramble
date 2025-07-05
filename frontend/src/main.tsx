import './api/config';

import { SessionProvider } from './context/SessionContext';
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import './index.css'
import App from './App.tsx'
import { Toaster } from 'sonner';



createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <App />
        <Toaster richColors />
      </QueryClientProvider>
    </SessionProvider>
  </StrictMode>,
)
