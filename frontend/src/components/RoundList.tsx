import { useQueryClient } from '@tanstack/react-query';
import {
    useStartRound,
    useRestartRound,
} from '../hooks/round';

import type { RoundDTO, Match, Team, Player } from '../api';

const CURRENT_ROUND_KEY = ['round', 'current'] as const;

export default function RoundList() {
    const queryClient = useQueryClient();
    const startRound = useStartRound();
    const restartRound = useRestartRound();

    /* ─── grab current round from cache ─── */
    const currentRound = queryClient.getQueryData<RoundDTO>(CURRENT_ROUND_KEY);

    /* ─── helpers ─── */
    const renderPlayer = (p: Player) => (
        <li key={p.id} className="pl-4 list-disc">
            {p.name} (lvl {p.level})
        </li>
    );

    const renderTeam = (team: Team, idx: number) => (
        <li key={idx} className="ml-4">
            <p className="font-semibold">Team {idx + 1}</p>
            <ul>{team.players?.map(renderPlayer)}</ul>
        </li>
    );

    const renderMatch = (match: Match, idx: number) => (
        <li key={idx} className="mb-4">
            <p className="font-bold">
                Match {idx + 1}
                {match.court ? ` — Court: ${match.court.name}` : ''}
            </p>
            <ul>{match.teams.map(renderTeam)}</ul>
        </li>
    );

    /* ─── render ─── */
    return (
        <div className="p-4 space-y-4">
            <h3 className="text-3xl font-bold">Current Round</h3>

            {currentRound ? (
                <ul>{currentRound.matches?.map(renderMatch)}</ul>
            ) : (
                <p>No round in progress.</p>
            )}

            <div className="space-x-4 pt-2">
                <button
                    className="px-4 py-2 bg-blue-500 text-white rounded"
                    onClick={() => startRound.mutate()}
                    disabled={startRound.isPending}
                >
                    Start Round
                </button>

                <button
                    className="px-4 py-2 bg-amber-500 text-white rounded"
                    onClick={() => restartRound.mutate()}
                    disabled={restartRound.isPending}
                >
                    Restart Round
                </button>
            </div>
        </div>
    );
}