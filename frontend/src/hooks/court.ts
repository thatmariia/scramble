import { useQueryClient } from '@tanstack/react-query';
import { useApiQuery } from './useApiQuery';
import { useApiMutation } from './useApiMutation';
import { useRequiredSessionName } from './useRequiredSession';
import {
    CourtService,
    type CourtDTO,
    type CourtCreate,
    type CourtBase
} from '../api';

export const COURTS_QUERY_KEY = ['courts'] as const;

// GET court (list all courts)
export function useCourts() {
    const active = useRequiredSessionName();

    return useApiQuery<CourtDTO[]>({
        queryKey: [...COURTS_QUERY_KEY, active],
        queryFn: () =>
            CourtService.listCourts({
                requestBody: { session_name: active } as CourtBase,
            }),
        enabled: !!active,
        staleTime: 0,
    });
}

// POST court (add new court)
export function useAddCourt() {
    const queryClient = useQueryClient();
    const active = useRequiredSessionName();

    return useApiMutation<CourtDTO, CourtCreate>({
        mutationFn: (data) =>
            CourtService.addCourt({
                requestBody: {
                    ...data,
                    session_name: active!,
                },
            }),
        onSuccess: (newCourt) => {
            queryClient.setQueryData<CourtDTO[]>(
                [...COURTS_QUERY_KEY, active],
                (old) => (old ? [...old, newCourt] : [newCourt])
            );
        },
    });
}

// DELETE court by ID
export function useDeleteCourt() {
    const queryClient = useQueryClient();
    const active = useRequiredSessionName();


    return useApiMutation<void, { courtId: string }>({
        mutationFn: ({ courtId }) =>
            CourtService.deleteCourtById({
                courtId,
                sessionName: active!,
            }),
        onSuccess: (_, { courtId }) => {
            queryClient.setQueryData<CourtDTO[]>(
                [...COURTS_QUERY_KEY, active],
                (old) => (old ? old.filter((c) => c.id !== courtId) : old)
            );
        },
    });
}

// DELETE all courts
export function useDeleteAllCourts() {
    const queryClient = useQueryClient();
    const active = useRequiredSessionName();

    return useApiMutation<void, void>({
        mutationFn: () =>
            CourtService.deleteAllCourts({
                sessionName: active!,
            }),
        onSuccess: () => {
            queryClient.setQueryData<CourtDTO[]>(
                [...COURTS_QUERY_KEY, active],
                []
            );
        },
    });
}