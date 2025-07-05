import { useState } from 'react';
import { useNewSession } from '../../hooks/session';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function NewSessionForm({ close, setActive }: Props) {
    const newSession = useNewSession();
    const [name, setName] = useState('');
    const [settings, setSettings] = useState('');

    return (
        <form
            className="space-y-2"
            onSubmit={(e) => {
                e.preventDefault();
                newSession.mutate(
                    { name: name || null, settings_path: settings || null },
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
                placeholder="Session name (optional)"
                value={name}
                onChange={(e) => setName(e.target.value)}
            />
            <input
                className="border rounded px-2 py-1 w-60"
                placeholder="Settings path (optional)"
                value={settings}
                onChange={(e) => setSettings(e.target.value)}
            />
            <button
                type="submit"
                className="px-3 py-1 bg-blue-500 text-white rounded"
                disabled={newSession.isPending}
            >
                Create
            </button>
        </form>
    );
}