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

export const SESSION_QUERY_KEY = ['session'] as const;

// GET session (load by name or latest)
export function useSession(name: string) {
    return useApiQuery<AppSessionDTO>({
        queryKey: [...SESSION_QUERY_KEY, name],
        queryFn: () => SessionService.loadSession({ name }),
        staleTime: Infinity,
      });
}

// GET session (load by name or latest), but with a mutation for refreshing
export function useLoadSession() {
    const queryClient = useQueryClient();

    return useApiMutation<AppSessionDTO, { name: string}>({
        mutationFn: ({ name }) => SessionService.loadSession({ name }),

        onSuccess: (sess, { name }) => {
            const key = [...SESSION_QUERY_KEY, name];
            queryClient.setQueryData(key, sess);

            // invalidate other state for that session
            queryClient.invalidateQueries({ queryKey: [...PLAYERS_QUERY_KEY, name] });
            queryClient.invalidateQueries({ queryKey: [...COURTS_QUERY_KEY, name] });
            queryClient.invalidateQueries({ queryKey: [...CURRENT_ROUND_KEY, name] });
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
            const name = newSession.session_name ?? 'no session name';

            queryClient.setQueryData<AppSessionDTO>(
                [...SESSION_QUERY_KEY, name],
                newSession,
            );

            // invalidate other session-scoped queries
            queryClient.invalidateQueries({ queryKey: [...PLAYERS_QUERY_KEY, name] });
            queryClient.invalidateQueries({ queryKey: [...COURTS_QUERY_KEY, name] });
            queryClient.invalidateQueries({ queryKey: [...CURRENT_ROUND_KEY, name] });
        },
    });
}