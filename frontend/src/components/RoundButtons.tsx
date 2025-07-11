import { useStartRound, useRestartRound, useRoundCount } from '../hooks/round';
import styles from './RoundButtons.module.css';


export function RoundButtons() {
    const startRound = useStartRound();
    const restartRound = useRestartRound();
    const { data: roundCount = 0, isLoading: isCountLoading } = useRoundCount();

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
                    disabled={restartRound.isPending || isCountLoading || roundCount === 0}
                >
                    restart round
                </button>
            </div>
        </div>
    );
}