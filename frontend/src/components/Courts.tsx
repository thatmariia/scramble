// src/components/courts/Courts.tsx
import { EntityListSection } from './shared/EntityListSection';
import { EntityListItem } from './shared/EntityListItem';
import { AddEntityButton } from './shared/AddEntityButton';

import { useCourts, useDeleteCourt } from '../hooks/court';
import { CourtForm } from './courts/CourtForm';
import type { CourtDTO } from '../api';

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
                    className="px-2 py-0.5 text-sm bg-red-400 text-white rounded"
                    onClick={() => deleteCourt.mutate({ courtId: c.id! })}
                    disabled={deleteCourt.isPending}
                >
                    Delete
                </button>
            }
        >
            {c.name}
        </EntityListItem>
    );

    return (
        <div className="p-4 space-y-6">
            <h3 className="text-3xl font-bold">Courts</h3>

            <EntityListSection
                title="All courts"
                items={courts}
                render={renderRow}
            />

            <AddEntityButton
                buttonLabel="+ Add court"
                form={<CourtForm onDone={() => {/* handled inside */ }} />}
            />
        </div>
    );
}