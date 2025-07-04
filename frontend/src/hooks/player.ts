// src/hooks/usePlayers.ts
import { useQuery } from '@tanstack/react-query';
import { PlayerService, type PlayerDTO, type PlayerListDTO } from '../api';


export function usePlayers() {
  return useQuery({
    queryKey: ['players'],
    queryFn: async () => {
      try {
        return await PlayerService.listPlayers();     // generated function
      } catch (err) {
        console.error('listPlayers failed:', err);
        throw err;   // re-throw so React-Query still handles it
      }
    },
    // retry: false,      // disable automatic retries while debugging
  });
}