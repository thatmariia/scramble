import { useQuery } from '@tanstack/react-query';
import { CURRENT_ROUND_KEY } from '../../hooks/round';
import type { RoundDTO, Match } from '../../api';
import { PanZoomWrapper } from '../../elements/PanZoomWrapper';
import styles from './Round.module.css';

interface Props {
    renderMatch: (match: Match, index: number) => React.ReactNode;
}

export function Round({ renderMatch }: Props) {
    const { data: round } = useQuery<RoundDTO>({ queryKey: CURRENT_ROUND_KEY });

    return (
        <div className={styles.roundContentWrapper}>
            <PanZoomWrapper>
                <div className={styles.roundContent}>
                {round?.matches?.length ? (
                    round.matches.map(
                        (match, idx) => renderMatch(match, idx)
                    )
                ) : (
                        <span>No round in progress.</span>
                )}
                </div>
            </PanZoomWrapper>
        </div>
    );
}