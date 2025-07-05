// src/components/courts/CourtForm.tsx
import { useState } from 'react';
import { useAddCourt } from '../../hooks/court';
import { EntityFormWrapper } from './shared/FormWrapper';

export function CourtForm({ onDone }: { onDone(): void }) {
    const addCourt = useAddCourt();
    const [name, setName] = useState('');

    return (
        <EntityFormWrapper
            onSubmit={() => {
                addCourt.mutate({ name }, {
                    onSuccess: () => {
                        setName('');
                        onDone();
                    },
                });
            }}
            onCancel={onDone}
            isSubmitting={addCourt.isPending}
        >
            <input
                className="input"
                placeholder="Court name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
            />
        </EntityFormWrapper>
    );
}