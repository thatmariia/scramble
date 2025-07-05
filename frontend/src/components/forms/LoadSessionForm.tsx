import { useState } from 'react';
import { useLoadSession } from '../../hooks/session';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function LoadSessionForm({ close, setActive }: Props) {
    const newSession = useLoadSession();
    const [name, setName] = useState('');

    return (
        <form
            className="space-y-2"
            onSubmit={(e) => {
                e.preventDefault();
                newSession.mutate(
                    { name: name || null},
                    {
                        onSuccess: () => {
                            setActive(name || null);
                            close();
                        },
                    },
                );
            }}
        >
            <input
                className="border rounded px-2 py-1 w-48"
                placeholder="Session name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
            />
            <button
                type="submit"
                className="px-3 py-1 bg-emerald-500 text-white rounded"
            >
                Load
            </button>
        </form>
    );
}