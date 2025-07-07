import { useQuery } from '@tanstack/react-query';
import { CURRENT_ROUND_KEY } from '../hooks/round';
import type { RoundDTO, Match } from '../api';
import { Round } from './round/Round';
import { PlayerStamp } from '../elements/PlayerStamp';
import { LEVEL_COLORS } from '../constants/levels';
import styles from './RoundViz.module.css';

interface MatchItemProps {
    match: Match;
    maxTeams: number;
    maxPlayers: number;
}

function MatchItem({
    match,
    maxTeams,
    maxPlayers
}: MatchItemProps) {
    const gridItems = [];

    for (let teamIdx = 0; teamIdx < maxTeams; teamIdx++) {
        const team = match.teams?.[teamIdx] ?? {};
        for (let playerIdx = 0; playerIdx < maxPlayers; playerIdx++) {
            const player = team?.players?.[playerIdx];
            gridItems.push(
                <div key={`${teamIdx}-${playerIdx}`} className={styles.playerCell}>
                    {player ? (
                        <PlayerStamp
                            tag={player.assignment?.trim() || 'n/a'}
                            color={LEVEL_COLORS[player.level]}
                        />
                    ) : (
                        <div className={styles.emptyCell}></div>
                    )}
                </div>
            );
        }
    }

    return (
        <div className={`card ${styles.court} sand`}>
            <div className={styles.header}>
                {match.court ? `court ${match.court.name}` : `unknown court`}
            </div>

            {/* <div className="card sand"> */}
                <div
                    className={styles.grid}
                    style={{
                        gridTemplateColumns: `repeat(${maxPlayers}, 3em)`,
                        gridTemplateRows: `repeat(${maxTeams}, 2em)`
                    }}
                >
                    {gridItems}
                </div>
            {/* </div> */}
        </div>
    );
}

export default function RoundList() {
    const { data: currentRound } = useQuery<RoundDTO>({ queryKey: CURRENT_ROUND_KEY });

    const matches = currentRound?.matches ?? [];

    // max number of teams per match
    const teamCounts = matches.map((m) => m.teams.length);
    const maxTeams = Math.max(...teamCounts);

    // max number of players per team
    const playerCounts = matches.flatMap((m) => m.teams.map((t) => t.players?.length ?? 0));
    const maxPlayers = Math.max(...playerCounts);

    return (
        <Round 
            renderMatch={(match, idx) => <MatchItem 
                key={idx} 
                match={match} 
                maxTeams={maxTeams}
                maxPlayers={maxPlayers}
            />} 
        />
    );
}