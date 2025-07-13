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
    onError,
    enabled = true,
    ...options
}: UseApiQueryOptions<TData>) {
    const randomId = Math.random().toString(36).substring(2, 15);
    return useQuery<TData, Error>({
        queryKey,
        queryFn: async () => {
            console.debug(randomId, '[useApiQuery] Executing query:', queryKey, 'enabled:', enabled);
            if (!enabled) {
                console.debug(randomId, '[useApiQuery] Query is disabled, returning rejected promise');
                // Never gets executed if enabled is false, but just in case
                return Promise.reject(new Error('Query disabled'));
            }
            try {
                console.debug(randomId, '[useApiQuery] Calling query function for:', queryKey);
                return await queryFn();
            } catch (err) {
                console.error(randomId, '[useApiQuery] Query failed:', queryKey, err);
                const error = err as Error;
                toast.error(`Query failed: ${error.message}`);
                onError?.(error);
                throw error;
            }
        },
        enabled,
        ...options,
    });
}