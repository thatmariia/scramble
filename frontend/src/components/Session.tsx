// src/components/Session.tsx
import { useState, useRef } from 'react';
import { useSessionName } from '../context/SessionContext';
import { useSession } from '../hooks/session';
import CustomDropdown from '../elements/CustomDropdown'; 
import NewSessionForm from './forms/NewSessionForm';
import LoadSessionForm from './forms/LoadSessionForm';
import styles from './Session.module.css';
import { Volleyball } from 'lucide-react';

export default function Session() {
    const { name: active, setName } = useSessionName();
    const { isLoading } = useSession(active);
    const [showMenu, setShowMenu] = useState(false);
    const menuButtonRef = useRef<HTMLButtonElement>(null);

    if (isLoading) return <div className={styles.loading}>Loading session…</div>;

    return (
        <header className={styles.sessionHeader}>
            <div className={styles.sessionInfo}>
                <span className={styles.name}>
                    {/* <Volleyball className="icon" /> */}
                    {active ?? 'No active session'}
                </span>
            </div>

            <div className={styles.menuWrapper}>
                <button
                    ref={menuButtonRef}
                    className={styles.menuToggle}
                    onClick={() => setShowMenu((v) => !v)}
                >
                    <span className={styles.menuTitle}>session</span>
                </button>
                <CustomDropdown
                    open={showMenu}
                    onClose={() => setShowMenu(false)}
                    triggerRef={menuButtonRef}
                >
                    <div className={styles.dropdown}>
                        <NewSessionForm close={() => setShowMenu(false)} setActive={setName} />
                        <LoadSessionForm close={() => setShowMenu(false)} setActive={setName} />
                    </div>
                </CustomDropdown>
            </div>
        </header>
    );
}