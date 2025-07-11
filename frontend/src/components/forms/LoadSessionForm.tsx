// src/components/forms/LoadSessionForm.tsx
import { useState } from 'react';
import { useLoadSession } from '../../hooks/session';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css'; 
import { toast } from 'sonner';

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function LoadSessionForm({ close, setActive }: Props) {
    const loadSession = useLoadSession();
    const [name, setName] = useState('');

    const handleSubmit = () => {
        const trimmed = name.trim();
        if (!trimmed) {
            toast.error('Please enter a session name');
            return;
        }

        loadSession.mutate(
            { name: trimmed },
            {
                onSuccess: () => {
                    setActive(trimmed);
                    close();
                },
                onError: () => {
                    toast.error(`Could not load session "${trimmed}"`);
                },
            }
        );
    };

    return (
        <div>
            <p className={styles.title}>
                Load a session
            </p>
            <EntityFormWrapper
                onSubmit={handleSubmit}
                onCancel={close}
                isSubmitting={loadSession.isPending}
                submitLabel="Load"
            >
                <input
                    className="input"
                    placeholder="Name (optional)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
            </EntityFormWrapper>
        </div>
    );
}