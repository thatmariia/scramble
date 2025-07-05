// src/components/Session.tsx
import { useState } from 'react';
import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import NewSessionForm from './forms/NewSessionForm';
import LoadSessionForm from './forms/LoadSessionForm';
import styles from './Session.module.css';

export default function Session() {
    const { name: active, setName } = useSessionName();
    const { isLoading } = useSession(active);
    const [showMenu, setShowMenu] = useState(false);

    if (isLoading) return <div className={styles.loading}>Loading session…</div>;

    return (
        <header className={styles.sessionHeader}>
            <div className={styles.sessionInfo}>
                <span className={styles.name}>{active ?? 'No active session'}</span>
            </div>

            <div className={styles.menuWrapper}>
                <button
                    className={styles.menuToggle}
                    onClick={() => setShowMenu((v) => !v)}
                >
                    <span className={styles.menuTitle}>session</span>
                </button>

                {showMenu && (
                    <div className={styles.dropdown}>
                        <NewSessionForm close={() => setShowMenu(false)} setActive={setName} />
                        <LoadSessionForm close={() => setShowMenu(false)} setActive={setName} />
                    </div>
                )}
            </div>
        </header>
    );
}