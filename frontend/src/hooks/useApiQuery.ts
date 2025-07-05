// src/hooks/useApiQuery.ts
import { useQuery, type UseQueryOptions, type QueryKey } from '@tanstack/react-query';
import { toast } from 'sonner';

type UseApiQueryOptions<TData> = Omit<
    UseQueryOptions<TData, Error>,    // all the usual options …
    'queryKey' | 'queryFn'            // …except the two we override
> & {
    /** React Query cache key */
    queryKey: QueryKey;
    /** Promise-returning service call */
    queryFn: () => Promise<TData>;
    /** Optional per-call error callback (since v5 removed the built-in one) */
    onError?: (error: Error) => void;
};

export function useApiQuery<TData>({
    queryKey,
    queryFn,
    onError,          // pull it out so we can call it manually
    ...options        // everything else goes straight through
}: UseApiQueryOptions<TData>) {
    return useQuery<TData, Error>({
        queryKey,
        // we intercept the error inside the query function itself
        queryFn: async () => {
            try {
                return await queryFn();
            } catch (err) {
                const error = err as Error;
                toast.error(`Query failed: ${error.message}`);
                onError?.(error);          // user-supplied callback, if any
                throw error;               // re-throw so React Query keeps state in sync
            }
        },
        ...options,                   // staleTime, gcTime, select, enabled, etc.
    });
}