import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import { useRequiredSessionName } from './useRequiredSession';
import {
  PlayerService,
  type PlayerListDTO,
  type PlayerCreate,
  type PlayerDTO,
} from '../api';

export const PLAYERS_QUERY_KEY = ['players'] as const; 

// GET player (list all players)
export function usePlayers() {
  const active = useRequiredSessionName();

  return useApiQuery<PlayerListDTO>({
    queryKey: [...PLAYERS_QUERY_KEY, active],
    queryFn: () =>
      PlayerService.listPlayers({
        sessionName: active,
      }),
    enabled: !!active,
    staleTime: 0,
  });
}

// POST player (add new player)
export function useAddPlayer() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<PlayerDTO, PlayerCreate>({
    mutationFn: (data) =>
      PlayerService.addPlayer({
        requestBody: data,
        sessionName: active,
      }),
    onSuccess: (newPlayer) => {
      queryClient.setQueryData<PlayerListDTO>(
        [...PLAYERS_QUERY_KEY, active],
        (old) =>
          old
            ? { ...old, active: [...old.active, newPlayer] }
            : { active: [newPlayer], resting: [] }
      );
    },
  });
}

// DELETE player by ID
export function useDeletePlayer() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<void, { playerId: string }>({
    mutationFn: ({ playerId }) =>
      PlayerService.deletePlayerById({
        playerId,
        sessionName: active,
      }),
    onSuccess: (_, { playerId }) => {
      queryClient.setQueryData<PlayerListDTO>(
        [...PLAYERS_QUERY_KEY, active],
        (old) =>
          old
            ? {
              ...old,
              active: old.active.filter((p) => p.id !== playerId),
              resting: old.resting.filter((p) => p.id !== playerId),
            }
            : old
      );
    },
  });
}

// DELETE all players
export function useDeleteAllPlayers() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<void, void>({
    mutationFn: () =>
      PlayerService.deleteAllPlayers({
        sessionName: active,
      }),
    onSuccess: () => {
      queryClient.setQueryData<PlayerListDTO>(
        [...PLAYERS_QUERY_KEY, active],
        { active: [], resting: [] }
      );
    },
  });
}

// PATCH player (update resting state of player)
export function useToggleRestPlayer() {
  const queryClient = useQueryClient();
  const active = useRequiredSessionName();

  return useApiMutation<PlayerListDTO, { playerId: string }>({
    mutationFn: ({ playerId }) =>
      PlayerService.toggleRestPlayer({
        playerId,
        sessionName: active,
      }),
    onSuccess: (updatedLists) => {
      queryClient.setQueryData<PlayerListDTO>(
        [...PLAYERS_QUERY_KEY, active],
        updatedLists
      );
    },
  });
}