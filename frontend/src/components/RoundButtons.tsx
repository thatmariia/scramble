import { useStartRound, useRestartRound } from '../hooks/round';
import styles from './RoundButtons.module.css';


export function RoundButtons() {

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
        </div>
    );
}