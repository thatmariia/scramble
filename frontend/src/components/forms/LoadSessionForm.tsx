// src/components/forms/LoadSessionForm.tsx
import { useState } from 'react';
import { useLoadSession } from '../../hooks/session';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css'; 

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function LoadSessionForm({ close, setActive }: Props) {
    const loadSession = useLoadSession();
    const [name, setName] = useState('');

    const handleSubmit = () => {
        loadSession.mutate(
            { name: name || null },
            {
                onSuccess: () => {
                    setActive(name || null);
                    close();
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