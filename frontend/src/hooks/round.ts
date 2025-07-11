import { useQueryClient } from '@tanstack/react-query';
import { QueryClient } from '@tanstack/react-query';
import { useApiMutation } from './useApiMutation';
import { useApiQuery } from './useApiQuery';
import { useRequiredSessionName } from './useRequiredSession';
import {
  RoundService,
  type RoundDTO,
} from '../api';


export const ROUND_QUERY_KEY = ['round'] as const;
export const CURRENT_ROUND_KEY = ['round', 'current'] as const; 
export const ROUND_COUNT_KEY = (sessionName: string) => ['round', 'count', sessionName] as const;
export const ROUND_BY_INDEX_KEY = (sessionName: string, index: number) =>
  ['round', 'by-index', sessionName, index] as const;


export function invalidateRoundQueries(queryClient: QueryClient, sessionName: string) {
  queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
  queryClient.invalidateQueries({ queryKey: ROUND_COUNT_KEY(sessionName) });

  queryClient.invalidateQueries({
    predicate: (query) =>
      Array.isArray(query.queryKey) &&
      query.queryKey[0] === 'round' &&
      query.queryKey[1] === 'by-index' &&
      query.queryKey[2] === sessionName,
  });
}


// GET number of rounds in a session
export function useRoundCount() {
  const sessionName = useRequiredSessionName();

  return useApiQuery<number>({
    queryKey: ROUND_COUNT_KEY(sessionName),
    queryFn: () => RoundService.getRoundCount({ sessionName }),
    enabled: !!sessionName,
    staleTime: Infinity,
  });
}

// GET round by index
export function useRoundByIndex(index: number) {
  const sessionName = useRequiredSessionName();

  return useApiQuery<RoundDTO>({
    queryKey: ROUND_BY_INDEX_KEY(sessionName, index),
    queryFn: () => RoundService.getRoundByIndex({ sessionName, index }),
    enabled: index != null && index >= 0 && !!sessionName,
  });
}

// POST round (start a new round) 
export function useStartRound() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<RoundDTO, void>({
    mutationFn: () => RoundService.startRound({ sessionName: active }),
    onSuccess: (newRound) => {
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY, newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
      invalidateRoundQueries(queryClient, active);
    },
  });
}

// POST round (restart round)
export function useRestartRound() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<RoundDTO, void>({
    mutationFn: () => RoundService.restartRound({ sessionName: active }),
    onSuccess: (newRound) => {
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY, newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
      invalidateRoundQueries(queryClient, active);
    },
  });
}

// DELETE round (undo last round)
export function useUndoRound() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<void, void>({
    mutationFn: () => RoundService.undoRound({ sessionName: active }),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: CURRENT_ROUND_KEY });
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
      invalidateRoundQueries(queryClient, active);
    },
  });
}