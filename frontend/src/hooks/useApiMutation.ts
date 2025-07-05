// src/hooks/useApiMutation.ts
import {
    useMutation,
    type UseMutationOptions,
    type MutationFunction,
} from '@tanstack/react-query';
import { toast } from 'sonner';
import { ApiError } from '../api'; // keep if you want ApiError-specific logic

/**
 * Generic mutation-wrapper options
 *
 * TData       – data returned from the server
 * TVariables  – shape of the payload you send
 * TContext    – optional React-Query context object
 */
export type UseApiMutationOptions<
    TData,
    TVariables,
    TContext = unknown,
> = Omit<
    UseMutationOptions<TData, Error, TVariables, TContext>,
    'mutationFn' | 'onError'
> & {
    /** Your service call (POST / PATCH / DELETE …) */
    mutationFn: MutationFunction<TData, TVariables>;
    /** Optional per-call handler after the toast shows */
    onError?: (
        error: Error,
        variables: TVariables,
        context: TContext | undefined,
    ) => void;
};

/**
 * Reusable mutation hook with global toast + optional local handler
 */
export function useApiMutation<
    TData,
    TVariables,
    TContext = unknown,
>({
    mutationFn,
    onError,
    ...options
}: UseApiMutationOptions<TData, TVariables, TContext>) {
    return useMutation<TData, Error, TVariables, TContext>({
        mutationFn: async (vars) => {
            // You *can* wrap the call in a try/catch here,
            // but letting React-Query catch and pass the error to onError
            // keeps retries / status tracking intact.
            return mutationFn(vars);
        },

        // Global toast, then delegate to any user-supplied handler
        onError: (error, vars, ctx) => {
            const message =
                error instanceof ApiError
                    ? error.body?.detail ?? error.message
                    : error.message;
            toast.error(`Action failed: ${message}`);

            // Call the caller’s own onError, if they provided one
            onError?.(error, vars, ctx);
        },

        ...options, // onSuccess, retry, invalidateQueries, etc.
    });
  }