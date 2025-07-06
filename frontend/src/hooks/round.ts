// src/hooks/rounds.ts
import { useQueryClient } from '@tanstack/react-query';
import { useApiMutation } from './useApiMutation';
import {
  RoundService,
  type RoundDTO,
} from '../api';


export const CURRENT_ROUND_KEY = ['round', 'current'] as const;

// POST round (start a new round)
export function useStartRound() {
  const queryClient = useQueryClient();

  return useApiMutation<RoundDTO, void>({
    mutationFn: () => RoundService.startRound(),

    onSuccess: (newRound) => {
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY, newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
    },
  });
}

// POST round (restart round)
export function useRestartRound() {
  const queryClient = useQueryClient();

  return useApiMutation<RoundDTO, void>({
    mutationFn: () => RoundService.restartRound(),

    onSuccess: (newRound) => {
      queryClient.setQueryData<RoundDTO>(CURRENT_ROUND_KEY, newRound);
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
    },
  });
}

// DELETE round (undo last round)
export function useUndoRound() {
  const queryClient = useQueryClient();

  return useApiMutation<void, void>({
    mutationFn: () => RoundService.undoRound(),

    onSuccess: () => {
      queryClient.removeQueries({ queryKey: CURRENT_ROUND_KEY });
      queryClient.invalidateQueries({ queryKey: CURRENT_ROUND_KEY });
    },
  });
}