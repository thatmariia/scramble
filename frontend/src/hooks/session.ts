// src/hooks/sessions.ts
import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import {
    SessionService,
    type AppSessionDTO,
    type SessionCreate,
} from '../api';
import { COURTS_QUERY_KEY } from './court';
import { PLAYERS_QUERY_KEY } from './player';
import { CURRENT_ROUND_KEY } from './round';

const SESSION_QUERY_KEY = ['session'] as const;

// GET session (load by name or latest)
export function useSession(name?: string | null) {
    return useApiQuery<AppSessionDTO>({
        queryKey: [...SESSION_QUERY_KEY, name ?? 'no session name'],
        queryFn: () => SessionService.loadSession({ name }),
        staleTime: Infinity
    });
}

// GET session (load by name or latest), but with a mutation for refreshing
export function useLoadSession() {
    const qc = useQueryClient();

    return useApiMutation<AppSessionDTO, { name?: string | null }>({
        mutationFn: ({ name }) => SessionService.loadSession({ name }),

        onSuccess: (sess, { name }) => {
            // write session into cache
            const key = [...SESSION_QUERY_KEY, name ?? 'no session name'];
            qc.setQueryData(key, sess);

            // fetch players / courts / round for that session
            qc.invalidateQueries({ queryKey: PLAYERS_QUERY_KEY });
            qc.invalidateQueries({ queryKey: COURTS_QUERY_KEY });
            qc.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
        },
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
                [...SESSION_QUERY_KEY, newSession?.session_name ?? 'no session name'],
                newSession,
            );
            // invalidate so they refetch for the new session
            queryClient.invalidateQueries({ queryKey: PLAYERS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: COURTS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
        },
    });
}