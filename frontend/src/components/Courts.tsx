// src/components/courts/Courts.tsx
import { EntityListSection } from './shared/EntityListSection';
import { EntityListItem } from './shared/EntityListItem';
import { AddEntityButton } from './shared/AddEntityButton';

import { useCourts, useDeleteCourt } from '../hooks/court';
import { CourtForm } from './forms/CourtForm';
import type { CourtDTO } from '../api';
import { Trash } from 'lucide-react';
import { Card } from './shared/Card';

export default function Courts() {
    /* Data + mutations */
    const { data: courts = [], isLoading } = useCourts();
    const deleteCourt = useDeleteCourt();

    /* Loading state */
    if (isLoading) return <p className="p-4">Loading…</p>;

    /* Row renderer */
    const renderRow = (c: CourtDTO) => (
        <EntityListItem
            key={c.id}
            primaryAction={null /* no toggle for courts */}
            dangerAction={
                <button
                    className="button danger"
                    onClick={() => deleteCourt.mutate({ courtId: c.id! })}
                    disabled={deleteCourt.isPending}
                >
                    <Trash className="icon" />
                </button>
            }
        >
            {c.name}
        </EntityListItem>
    );

    return (
        <Card title="Courts">
            <EntityListSection
                items={courts}
                render={renderRow}
            />

            <AddEntityButton
                entity="court"
                renderForm={(close) => <CourtForm onDone={close} />}
            />
        </Card>
    );
}