// src/hooks/players.ts
import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import {
  PlayerService,
  type PlayerListDTO,
  type PlayerCreate,
  type PlayerDTO,
} from '../api';

export const PLAYERS_QUERY_KEY = ['players'] as const;

// GET player (list all players)
export function usePlayers() {
  return useApiQuery<PlayerListDTO>({
    queryKey: PLAYERS_QUERY_KEY,
    queryFn: () => PlayerService.listPlayers(),
    staleTime: 60_000,
  });
}

// POST player (add new player)
export function useAddPlayer() {
  const queryClient = useQueryClient();

  return useApiMutation<PlayerDTO, PlayerCreate>({
    mutationFn: (data) => PlayerService.addPlayer({ requestBody: data }),

    onSuccess: (newPlayer) => {
      queryClient.setQueryData<PlayerListDTO>(PLAYERS_QUERY_KEY, (old) =>
        old
          ? { ...old, active: [...old.active, newPlayer] }
          : { active: [newPlayer], resting: [] },
      );
    },
  });
}

// DELETE player by ID
export function useDeletePlayer() {
  const queryClient = useQueryClient();

  return useApiMutation<void, { playerId: string }>({
    mutationFn: ({ playerId }) =>
      PlayerService.deletePlayerById({ playerId }),

    onSuccess: (_, { playerId }) => {
      queryClient.setQueryData<PlayerListDTO>(PLAYERS_QUERY_KEY, (old) =>
        old
          ? {
            ...old,
            active: old.active.filter((p) => p.id !== playerId),
            resting: old.resting.filter((p) => p.id !== playerId),
          }
          : old,
      );
    },
  });
}

// DELETE all players
export function useDeleteAllPlayers() {
  const queryClient = useQueryClient();

  return useApiMutation<void, void>({
    mutationFn: () => PlayerService.deleteAllPlayers(),

    onSuccess: () => {
      queryClient.setQueryData<PlayerListDTO>(PLAYERS_QUERY_KEY, {
        active: [],
        resting: [],
      });
    },
  });
}

// PATCH player (update resting state of player)
export function useToggleRestPlayer() {
  const queryClient = useQueryClient();

  return useApiMutation<PlayerListDTO, { playerId: string }>({
    mutationFn: ({ playerId }) =>
      PlayerService.toggleRestPlayer({ playerId }),

    onSuccess: (updatedLists) => {
      queryClient.setQueryData<PlayerListDTO>(
        PLAYERS_QUERY_KEY,
        updatedLists,
      );
    },
  });
}