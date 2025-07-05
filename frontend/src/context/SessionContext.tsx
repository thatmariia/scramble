// src/context/SessionContext.tsx
import { createContext, useContext, useState, type ReactNode } from 'react';

type SessionCtx = {
    name: string | null;
    setName: (n: string | null) => void;
};

const SessionContext = createContext<SessionCtx | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
    const [name, setName] = useState<string | null>(null);
    return (
        <SessionContext.Provider value={{ name, setName }}>
            {children}
        </SessionContext.Provider>
    );
}

export const useSessionName = () => {
    const ctx = useContext(SessionContext);
    if (!ctx) throw new Error('useSessionName must be inside SessionProvider');
    return ctx;
};