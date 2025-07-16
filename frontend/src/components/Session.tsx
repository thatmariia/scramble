import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import styles from './Session.module.css';

export default function Session() {
    const { name: active, setName } = useSessionName();
    const { isLoading } = active ? useSession(active) : { isLoading: false }; 

    if (!active) {
        return (
            <header className={styles.sessionHeader}>
                <div className={styles.sessionInfo}>
                    <span className={styles.name}>No active session</span>
                </div>
            </header>
        );
    }

    if (isLoading) {
        return <div className={styles.loading}>Loading session…</div>;
    }

    return (
        <header className={styles.sessionHeader}>
            <div className={styles.sessionInfo}>
                <span className={styles.name}>
                    {active ?? 'No active session'}
                </span>
            </div>
        </header>
    );
}