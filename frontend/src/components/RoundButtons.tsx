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
    const [prevIndex, setPrevIndex] = useState<number | null>(null);

    const startRound = useStartRound({
        onSuccess: (newCount) => {
            setSelectedIndex(newCount);
        },
    });
    const restartRound = useRestartRound();
    const undoRound = useUndoRound({
        onQuery: () => {
            setPrevIndex(selectedIndex);
            // setSelectedIndex(null);
            console.log('[RoundButtons] undoing round, setting selectedIndex to null');
        },
        onSuccess: (newCount) => {
            setSelectedIndex(newCount > 0 ? newCount : null);
        },
        onError: (error) => {
            console.error('Failed to undo round:', error);
            setSelectedIndex(prevIndex);
        }
    });

    const { data: roundCount = 0, isLoading: isCountLoading } = useRoundCount();
    const queryClient = useQueryClient();

    // select last round by default when roundCount changes
    useEffect(() => {
        if (roundCount > 0) {
            setSelectedIndex((prev) => {
                if (prev === null || prev > roundCount) return roundCount;
                return prev;
            });
        } else {
            setSelectedIndex(null);
        }
    }, [roundCount]);

    const effectiveIndex = selectedIndex !== null ? selectedIndex - 1 : -1;
    const isValidIndex = effectiveIndex >= 0 && effectiveIndex < roundCount;
    console.log('[RoundButtons] effectiveIndex:', effectiveIndex, 'isValidIndex:', isValidIndex);

    const {
        data: selectedRound,
        isLoading: isRoundLoading,
        isError: isRoundError,
    } = useRoundByIndex(effectiveIndex);

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
    
    const isLastRound = selectedIndex === roundCount;

    return (
        <div>
            <div className={styles.actionButtons}>
                {/* {roundCount > 0 && (
                    <CustomSelect<number>
                        value={selectedIndex ?? 0}
                        options={options}
                        onChange={(val) => setSelectedIndex(val)}
                    />
                )} */}
                <CustomSelect<number>
                    value={selectedIndex ?? 0}
                    options={options}
                    onChange={(val) => setSelectedIndex(val)}
                    fixedWidth="8em"
                />

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
                    disabled={restartRound.isPending || !isLastRound || roundCount === 0 || isRoundLoading}
                >
                    restart round
                </button>

                <button
                    className="button danger"
                    onClick={() => undoRound.mutate()}
                    disabled={restartRound.isPending || !isLastRound || roundCount === 0 || isRoundLoading}
                >
                    undo round
                </button>
            </div>
        </div>
    );
}