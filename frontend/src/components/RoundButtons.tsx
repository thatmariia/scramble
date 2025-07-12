import { useState, useEffect } from 'react';
import { useSessionName } from '../context/SessionContext';
import { useQueryClient } from '@tanstack/react-query';
import {
    CURRENT_ROUND_KEY,
    useStartRound,
    useRestartRound,
    useUndoRound,
    useRoundCount,
    useRoundByIndex,
} from '../hooks/round';
import { CustomSelect } from '../elements/CustomSelect';
import styles from './RoundButtons.module.css';

export function RoundButtons() {
    const { name: sessionName } = useSessionName();
    const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

    const startRound = useStartRound();
    const restartRound = useRestartRound();
    const undoRound = useUndoRound();

    const { data: roundCount = 0, isLoading: isCountLoading } = useRoundCount();
    const queryClient = useQueryClient();

    // Select last round by default when roundCount changes
    useEffect(() => {
        if (roundCount > 0) {
            setSelectedIndex((prev) => (prev === null ? roundCount : prev));
        } else {
            setSelectedIndex(null);
        }
    }, [roundCount]);

    const {
        data: selectedRound,
        isLoading: isRoundLoading,
        isError: isRoundError,
    } = useRoundByIndex(selectedIndex !== null ? selectedIndex - 1 : -1);

    useEffect(() => {
        if (sessionName && selectedRound) {
            queryClient.setQueryData(CURRENT_ROUND_KEY(sessionName), selectedRound);
        }
    }, [selectedRound, queryClient]);

    const options =
        roundCount > 0
            ? Array.from({ length: roundCount }, (_, i) => ({
                label: `round ${i + 1}`,
                value: i + 1,
            }))
            : [];

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

                {!isCountLoading && roundCount > 0 && (
                    <>
                        <button
                            className="button primary"
                            onClick={() => restartRound.mutate()}
                            disabled={restartRound.isPending}
                        >
                            restart round
                        </button>
                        <button
                            className="button danger"
                            onClick={() => undoRound.mutate()}
                            disabled={undoRound.isPending}
                        >
                            undo round
                        </button>
                    </>
                )}

                {roundCount > 0 && (
                    <CustomSelect<number>
                        value={selectedIndex ?? 0}
                        options={options}
                        onChange={(val) => setSelectedIndex(val)}
                    />
                )}
            </div>
        </div>
    );
}