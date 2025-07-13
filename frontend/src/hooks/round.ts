import { useQueryClient } from '@tanstack/react-query';
import { QueryClient } from '@tanstack/react-query';
import { useApiMutation } from './useApiMutation';
import { useApiQuery } from './useApiQuery';
import { useRequiredSessionName } from './useRequiredSession';
import {
  RoundService,
  type RoundDTO,
} from '../api';
import { toast } from 'sonner';


export const ROUND_QUERY_KEY = ['round'] as const;
export const CURRENT_ROUND_KEY = (sessionName: string) =>
  ['round', 'current', sessionName] as const;
export const ROUND_COUNT_KEY = (sessionName: string) => ['round', 'count', sessionName] as const;
export const ROUND_BY_INDEX_KEY = (sessionName: string, index: number) =>
  ['round', 'by-index', sessionName, index] as const;


export function invalidateRoundQueries(queryClient: QueryClient, sessionName: string) {
  queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY(sessionName) });
  queryClient.invalidateQueries({ queryKey: ROUND_COUNT_KEY(sessionName) });

  queryClient.invalidateQueries({
    predicate: (query) =>
      Array.isArray(query.queryKey) &&
      query.queryKey[0] === 'round' &&
      query.queryKey[1] === 'by-index' &&
      query.queryKey[2] === sessionName,
  });
}

// GET current round (from cache if set, else load last round)
export function useCurrentRoundIndex() {
  const { data: roundCount, isLoading, error } = useRoundCount();

  if (isLoading || roundCount === undefined) {
    return { lastIndex: undefined, isLoading: true, error };
  }

  const lastIndex = roundCount > 0 ? roundCount - 1 : -1;
  return { lastIndex, isLoading: false, error: null };
}

export function useCurrentRound() {
  const sessionName = useRequiredSessionName();
  const { lastIndex, isLoading } = useCurrentRoundIndex();

  const enabled = !!sessionName && lastIndex !== undefined && lastIndex >= 0;

  console.log('[useCurrentRound] sessionName:', sessionName, 'lastIndex:', lastIndex, 'enabled:', enabled);

  return useApiQuery<RoundDTO>({
    queryKey: CURRENT_ROUND_KEY(sessionName),
    queryFn: () => RoundService.getRoundByIndex({ sessionName, index: lastIndex! }),
    enabled,
    staleTime: 0,
  });
}


// GET number of rounds in a session
export function useRoundCount() {
  const sessionName = useRequiredSessionName();

  return useApiQuery<number>({
    queryKey: ROUND_COUNT_KEY(sessionName),
    queryFn: () => RoundService.getRoundCount({ sessionName }),
    enabled: !!sessionName,
    staleTime: 0,
  });
}

// GET round by index
// inside useRound.ts
export function useRoundByIndex(index: number) {
  const sessionName = useRequiredSessionName();
  const enabled = index >= 0 && !!sessionName;

  console.log('[useRoundByIndex] sessionName:', sessionName, 'index:', index, 'enabled:', enabled);

  const key = ROUND_BY_INDEX_KEY(sessionName, index);
  return useApiQuery<RoundDTO>({
    queryKey: key,
    queryFn: () => RoundService.getRoundByIndex({ sessionName, index }),
    enabled,
  });
}

// POST round (start a new round) 
export function useStartRound() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<RoundDTO, void>({
    mutationFn: () => RoundService.startRound({ sessionName: active }),
    onSuccess: (newRound) => {
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY(active), newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY(active) });
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
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY(active), newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY(active) });
      invalidateRoundQueries(queryClient, active);
    },
  });
}

// DELETE round (undo last round)
export function useUndoRound(opts?: {
  onQuery?: () => void;
  onSuccess?: (newCount: number) => void;
  onError?: (error: Error) => void;
}) {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<number, void>({
    mutationFn: () => {
      opts?.onQuery?.();
      return RoundService.undoRound({ sessionName: active });
    },
    onError: (error) => {
      opts?.onError?.(error);
    },
    onSuccess: async (newCount) => {
      // invalidateRoundQueries(queryClient, active);

      // update cached round count
      queryClient.setQueryData(ROUND_COUNT_KEY(active), newCount);

      const lastIndex = newCount > 0 ? newCount - 1 : -1;

      if (lastIndex >= 0) {
        const lastRound = await RoundService.getRoundByIndex({ sessionName: active, index: lastIndex });
        queryClient.setQueryData(CURRENT_ROUND_KEY(active), lastRound);
      } else {
        queryClient.removeQueries({ queryKey: CURRENT_ROUND_KEY(active) });
      }

      opts?.onSuccess?.(newCount);
    },
  });
}