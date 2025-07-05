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
import styles from './Card.module.css';
import { Trash, Pause, Play } from 'lucide-react';

export default function Players() {
    const { data, isLoading } = usePlayers();
    const deletePlayer = useDeletePlayer();
    const toggleRest = useToggleRestPlayer();

    if (isLoading) return <p className="p-4">Loading…</p>;

    const renderRow = (active: boolean) => (p: PlayerDTO) => (
        <EntityListItem
            key={p.id} 
            primaryAction={
                <button
                    className="button ghost"
                    onClick={() => toggleRest.mutate({ playerId: p.id! })}
                    disabled={toggleRest.isPending}
                >
                    {active ? (
                        <Pause className="icon" />
                    ) : (
                        <Play className="icon" />
                    )}
                </button>
            }
            dangerAction={
                <button
                    className="button danger"
                    onClick={() => deletePlayer.mutate({ playerId: p.id! })}
                    disabled={deletePlayer.isPending}
                >
                    <Trash className="icon" />
                </button>
            }
        >
            {p.name} (lvl&nbsp;{p.level}) — #{p.assignment ?? 'no ass'}
        </EntityListItem>
    );

    return (
        <div className={styles.card}>
            <span className={styles.title}>Players</span>

            <EntityListSection
                title="Active"
                items={data?.active ?? []}
                render={renderRow(true)}
            />

            <EntityListSection
                title="Resting"
                items={data?.resting ?? []}
                render={renderRow(false)}
            />

            <AddEntityButton
                entity="player"
                renderForm={(close) => <PlayerForm onDone={close} />}
            />
        </div>
    );
  }