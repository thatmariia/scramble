// src/hooks/courts.ts
import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import {
    CourtService,
    type CourtDTO,
    type CourtCreate,
} from '../api';

export const COURTS_QUERY_KEY = ['courts'] as const;

// GET court (list all courts)
export function useCourts() {
    return useApiQuery<CourtDTO[]>({
        queryKey: COURTS_QUERY_KEY,
        queryFn: () => CourtService.listCourts(),
        staleTime: 60_000,
    });
}

// POST court (add new court)
export function useAddCourt() {
    const queryClient = useQueryClient();

    return useApiMutation<CourtDTO, CourtCreate>({
        mutationFn: (data) => CourtService.addCourt({ requestBody: data }),

        onSuccess: (newCourt) => {
            queryClient.setQueryData<CourtDTO[]>(COURTS_QUERY_KEY, (old) =>
                old ? [...old, newCourt] : [newCourt],
            );
        },
    });
}

// DELETE court by ID
export function useDeleteCourt() {
    const queryClient = useQueryClient();

    return useApiMutation<void, { courtId: string }>({
        mutationFn: ({ courtId }) => CourtService.deleteCourtById({ courtId }),

        onSuccess: (_, { courtId }) => {
            queryClient.setQueryData<CourtDTO[]>(COURTS_QUERY_KEY, (old) =>
                old ? old.filter((c) => c.id !== courtId) : old,
            );
        },
    });
}

// DELETE all courts
export function useDeleteAllCourts() {
    const queryClient = useQueryClient();

    return useApiMutation<void, void>({
        mutationFn: () => CourtService.deleteAllCourts(),

        onSuccess: () => {
            queryClient.setQueryData<CourtDTO[]>(COURTS_QUERY_KEY, []);
        },
    });
}