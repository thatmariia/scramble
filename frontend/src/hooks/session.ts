// src/hooks/sessions.ts
import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import {
    SessionService,
    type AppSessionDTO,
    type SessionCreate,
} from '../api';

const SESSION_QUERY_KEY = ['session'] as const;

// GET session (load by name or latest)
export function useSession(name?: string | null) {
    return useApiQuery<AppSessionDTO>({
        queryKey: [...SESSION_QUERY_KEY, name ?? 'latest'],
        queryFn: () => SessionService.loadSession({ name }),
        staleTime: 60_000,
    });
}

// POST session (create new session)
export function useNewSession() {
    const queryClient = useQueryClient();

    return useApiMutation<AppSessionDTO, SessionCreate>({
        mutationFn: (data) =>
            SessionService.newSession({ requestBody: data }),

        onSuccess: (newSession) => {
            // Put the freshly-created session into cache
            queryClient.setQueryData<AppSessionDTO>(
                [...SESSION_QUERY_KEY, newSession?.name ?? 'latest'],
                newSession,
            );
            // Optional: invalidate players / courts so they refetch for the new session
            queryClient.invalidateQueries({ queryKey: ['players'] });
            queryClient.invalidateQueries({ queryKey: ['courts'] });
        },
    });
}