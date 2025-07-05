// src/components/courts/CourtForm.tsx
import { useState } from 'react';
import { useAddCourt } from '../../hooks/court';

export function CourtForm({ onDone }: { onDone(): void }) {
    const addCourt = useAddCourt();
    const [name, setName] = useState('');

    return (
        <form
            className="space-x-2"
            onSubmit={(e) => {
                e.preventDefault();
                addCourt.mutate(
                    { name },
                    { onSuccess: () => { setName(''); onDone(); } },
                );
            }}
        >
            <input
                className="border rounded px-2 py-1 w-48"
                placeholder="Court name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
            />
            <button
                type="submit"
                className="px-3 py-1 bg-blue-500 text-white rounded"
                disabled={addCourt.isPending}
            >
                Add
            </button>
        </form>
    );
}