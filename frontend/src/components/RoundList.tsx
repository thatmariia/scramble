import type { Match, Team, Player } from '../api';
import { Round } from './round/Round';

function PlayerItem({ player }: { player: Player }) {
    return (
        <li className="pl-4 list-disc">
            {player.name} (lvl {player.level})
        </li>
    );
}

function TeamItem({ team, index }: { team: Team; index: number }) {
    return (
        <li className="ml-4">
            <p className="font-semibold">Team {index + 1}</p>
            <ul>{team.players?.map((p) => <PlayerItem key={p.id} player={p} />)}</ul>
        </li>
    );
}

function MatchItem({ match, index }: { match: Match; index: number }) {
    return (
        <ul className="space-y-4">
            <li className="mb-4">
                <p className="font-bold">
                    Match {index + 1}
                    {match.court ? ` — Court: ${match.court.name}` : ''}
                </p>
                <ul>{match.teams.map((t, i) => <TeamItem key={i} team={t} index={i} />)}</ul>
            </li>
        </ul>
    );
}

export default function RoundList() {
    return (
        <Round renderMatch={(match, idx) => <MatchItem key={idx} match={match} index={idx} />} />
    );
}