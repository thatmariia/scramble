import { useCurrentRound } from '../../hooks/round';
import type { RoundDTO, Match } from '../../api';
import { PanZoomWrapper } from '../../elements/PanZoomWrapper';
import styles from './Round.module.css';

interface Props {
    renderMatch: (match: Match, index: number) => React.ReactNode;
}

export function Round({ renderMatch }: Props) {
    const { data: round, isLoading, isError } = useCurrentRound();


    return (
        <div className={styles.roundContentWrapper}>
            <PanZoomWrapper>
                <div className={styles.roundContent}>
                    {isLoading ? (
                        <span>Loading round…</span>
                    ) : isError || !round?.matches?.length ? (
                        <span>No round in progress.</span>
                    ) : (
                        round.matches.map((match, idx) => renderMatch(match, idx))
                    )}
                </div>
            </PanZoomWrapper>
        </div>
    );
}