// src/components/players/PlayerForm.tsx
import { useState } from 'react';
import type { Level } from '../../api';
import { useAddPlayer } from '../../hooks/player';

export function PlayerForm({ onDone }: { onDone(): void }) {
    const addPlayer = useAddPlayer();
    const [name, setName] = useState('');
    const [level, setLevel] = useState<Level>(3 as Level);

    return (
        <form
            className="space-x-2"
            onSubmit={(e) => {
                e.preventDefault();
                addPlayer.mutate(
                    { name, level },
                    {
                        onSuccess: () => {
                            setName('');
                            setLevel(3 as Level);
                            onDone();
                        },
                    },
                );
            }}
        >
            <input
                className="border rounded px-2 py-1 w-40"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
            />
            <select
                className="border rounded px-2 py-1"
                value={level}
                onChange={(e) => setLevel(Number(e.target.value) as Level)}
            >
                {[1, 2, 3, 4, 5].map((lvl) => (
                    <option key={lvl}>{lvl}</option>
                ))}
            </select>
            <button
                type="submit"
                className="px-3 py-1 bg-blue-500 text-white rounded"
                disabled={addPlayer.isPending}
            >
                Add
            </button>
        </form>
    );
}