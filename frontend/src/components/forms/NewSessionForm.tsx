import { useState } from 'react';
import { useNewSession } from '../../hooks/session';
import { EntityFormWrapper } from './shared/FormWrapper';
import styles from './Form.module.css'; 

interface Props {
    close(): void;
    setActive: (name: string | null) => void;
}

export default function NewSessionForm({ close, setActive }: Props) {
    const newSession = useNewSession();
    const [name, setName] = useState('');
    const [settings, setSettings] = useState('');

    const handleSubmit = () => {
        newSession.mutate(
            { name: name || "", settings_path: settings || null },
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
                Create a new session
            </p>
            <EntityFormWrapper
                onSubmit={handleSubmit}
                onCancel={close}
                isSubmitting={newSession.isPending}
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