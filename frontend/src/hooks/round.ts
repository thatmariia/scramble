import { useQueryClient } from '@tanstack/react-query';
import { useApiMutation } from './useApiMutation';
import { useApiQuery } from './useApiQuery';
import { useRequiredSessionName } from './useRequiredSession';
import {
  RoundService,
  type RoundDTO,
} from '../api';


const ROUND_QUERY_KEY = ['round'] as const;
export const CURRENT_ROUND_KEY = ['round', 'current'] as const; 
export const ROUND_COUNT_KEY = ['round', 'count'] as const;
export const ROUND_BY_INDEX_KEY = (index: number) =>
  ['round', 'by-index', index] as const;


// GET number of rounds in a session
export function useRoundCount() {
  const sessionName = useRequiredSessionName();

  return useApiQuery<number>({
    queryKey: ROUND_COUNT_KEY,
    queryFn: () => RoundService.getRoundCount({ sessionName }),
  });
}

// GET round by index
export function useRoundByIndex(index: number) {
  const sessionName = useRequiredSessionName();

  return useApiQuery<RoundDTO>({
    queryKey: ROUND_BY_INDEX_KEY(index),
    queryFn: () => RoundService.getRoundByIndex({ sessionName, index }),
    enabled: index != null && index >= 0, // optional guard
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
      queryClient.invalidateQueries({ queryKey: ROUND_QUERY_KEY });
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
      queryClient.invalidateQueries({ queryKey: ROUND_QUERY_KEY });
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
      queryClient.invalidateQueries({ queryKey: ROUND_QUERY_KEY });
    },
  });
}