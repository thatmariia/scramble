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
import { PlayerStamp } from '../elements/PlayerStamp';
import type { PlayerDTO } from '../api';
import { Trash, Pause, Play } from 'lucide-react';
import { LEVEL_COLORS } from '../constants/levels';
import { Card } from './shared/Card';
import styles from './Players.module.css';

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
                    className="button danger ghost"
                    onClick={() => deletePlayer.mutate({ playerId: p.id! })}
                    disabled={deletePlayer.isPending}
                >
                    <Trash className="icon" />
                </button>
            }
        > 
            <div className={styles.infoWrapper}>
                <PlayerStamp tag={p.assignment?.trim() || "n/a"} color={LEVEL_COLORS[p.level]} />
                {p.name}
            </div>
        </EntityListItem>
    );

    return (
        <Card title="Players">

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
        </Card>
    );
}