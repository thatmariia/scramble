// src/context/SessionContext.tsx
import {
    createContext, useContext, useState, useEffect, type ReactNode,
} from 'react';
import { queryClient } from '../lib/queryClient';
import {
    SessionService,
    type AppSessionDTO,
} from '../api';
import { SESSION_QUERY_KEY } from '../hooks/session';

const STORAGE_KEY = 'scramble:activeSession';

type SessionCtx = {
    name: string | null;
    setName: (n: string | null) => void;
};

const SessionContext = createContext<SessionCtx | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
    //  initialise from localStorage 
    const [name, setName] = useState<string | null>(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored || null;
    });

    // persist whenever it changes
    useEffect(() => {
        if (name) localStorage.setItem(STORAGE_KEY, name);
        else localStorage.removeItem(STORAGE_KEY);
    }, [name]);

    // fetch latest once if nothing stored
    useEffect(() => {
        if (name !== null) return; 

        (async () => {
            try {
                const latest: AppSessionDTO =
                    await SessionService.loadSession({ name: undefined });

                // write to React-Query cache so hooks see it
                queryClient.setQueryData(
                    [...SESSION_QUERY_KEY, latest.session_name ?? 'no session name'],
                    latest,
                );

                setName(latest.session_name ?? null);  // update context + localStorage
            } catch (err) {
                // 404 = no sessions yet - stay null; other errors you can log
                console.warn('No latest session found:', err);
            }
        })();
    }, [name]);

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