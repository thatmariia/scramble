import { useQuery } from '@tanstack/react-query';
import { useStartRound, useRestartRound, CURRENT_ROUND_KEY } from '../../hooks/round';
import type { RoundDTO, Match } from '../../api';
import styles from './Round.module.css';

interface Props {
    renderMatch: (match: Match, index: number) => React.ReactNode;
}

export function Round({ renderMatch }: Props) {
    const { data: round } = useQuery<RoundDTO>({ queryKey: CURRENT_ROUND_KEY });

    const startRound = useStartRound();
    const restartRound = useRestartRound();

    return (
        <div>
            <div className={styles.actionButtons}>
                <button
                    className="button primary"
                    onClick={() => startRound.mutate()}
                    disabled={startRound.isPending}
                >
                    start round
                </button>
                <button
                    className="button primary"
                    onClick={() => restartRound.mutate()}
                    disabled={restartRound.isPending}
                >
                    restart round
                </button>
            </div>
            <div className={styles.roundContentWrapper}>
                {round?.matches?.length ? (
                    round.matches.map((match, idx) => renderMatch(match, idx))
                ) : (
                        <span>No round in progress.</span>
                )}
            </div>
        </div>
    );
}