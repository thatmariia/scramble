// src/components/players/Players.tsx
import {
    usePlayers,
    useDeletePlayer,
    useToggleRestPlayer,
} from '../hooks/player';
import { EntityListSection } from './shared/EntityListSection';
import { EntityListItem } from './shared/EntityListItem';
import { AddEntityButton } from './shared/AddEntityButton';
import { PlayerForm } from './forms/PlayerForm';
import type { PlayerDTO } from '../api';

export default function Players() {
    const { data, isLoading } = usePlayers();
    const deletePlayer = useDeletePlayer();
    const toggleRest = useToggleRestPlayer();

    if (isLoading) return <p className="p-4">Loading…</p>;

    const renderRow = (bg: string) => (p: PlayerDTO) => (
        <EntityListItem
            key={p.id} 
            primaryAction={
                <button
                    className="button ghost"
                    onClick={() => toggleRest.mutate({ playerId: p.id! })}
                    disabled={toggleRest.isPending}
                >
                    Toggle
                </button>
            }
            dangerAction={
                <button
                    className="button danger"
                    onClick={() => deletePlayer.mutate({ playerId: p.id! })}
                    disabled={deletePlayer.isPending}
                >
                    Delete
                </button>
            }
        >
            {p.name} (lvl&nbsp;{p.level}) — #{p.assignment ?? '–'}
        </EntityListItem>
    );

    return (
        <div className="p-4 space-y-6">
            <h3 className="text-3xl font-bold">Players</h3>

            <EntityListSection
                title="Active"
                items={data?.active ?? []}
                render={renderRow('bg-gray-100')}
            />

            <EntityListSection
                title="Resting"
                items={data?.resting ?? []}
                render={renderRow('bg-gray-50')}
            />

            <AddEntityButton
                entity="player"
                renderForm={(close) => <PlayerForm onDone={close} />}
            />
        </div>
    );
  }